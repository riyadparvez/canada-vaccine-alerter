from db import *

import emoji
import nltk
import pickle
import re
import sys
# import spacy
from loguru import logger
from nltk.tokenize import word_tokenize
from sqlalchemy import func

nltk.download('punkt')

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True, format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)

# nlp = spacy.load("en_core_web_trf")
PROVINCES = ('AB', 'ON', 'MB', 'BC', 'QC', 'SK', 'NB', 'NS', 'PEI',)

with open('FSA.pickle', 'rb') as handle:
    FSA_SET = pickle.load(handle)

with open('cities.pickle', 'rb') as handle:
    CITY_SET = pickle.load(handle)

with open('fsa-city-dict.pickle', 'rb') as handle:
    FSA_CITY_DICT = pickle.load(handle)

def is_int(number_str):
    try:
        n = int(number_str)
        return True
    except Exception as e:
        return False

def cleaner(tweet):
    tweet = re.sub("@[A-Za-z0-9]+","",tweet) #Remove @ sign
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) #Remove http links
    tweet = " ".join(tweet.split())
    tweet = ''.join(c for c in tweet if c not in emoji.UNICODE_EMOJI) #Remove Emojis
    tweet = tweet.replace("#", "").replace("_", " ") #Remove hashtag sign but keep the text
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet))
    return tweet

def process_tweet(tweet_obj):
    try:
        logger.debug(f"Starting processing tweet: {tweet_obj.id} created_at: {tweet_obj.created_at}")
        # place = tweet_obj._json["place"]
        # entities = tweet_obj._json["entities"]

        tweet_url = f"https://twitter.com/twitter/statuses/"

        if "full_text" in tweet_obj._json:
            original_tweet_text = tweet_obj._json["full_text"]
        elif "full_text" in tweet_obj._json['extended_tweet']:
            original_tweet_text = tweet_obj._json['extended_tweet']["full_text"]
        
        if original_tweet_text.startswith("@"):
            logger.info(f"Skipping tweet because it's a reply: {tweet_obj.id} created_at: {tweet_obj.created_at}\n{original_tweet_text}")
            return

        province = original_tweet_text[:4][1:-1]
        province = province if province in PROVINCES else None

        tweet = original_tweet_text[5:]
        print(tweet)
        age_groups = re.match(r'^([\s\d]+)+$', original_tweet_text)

        tweet_text = cleaner(original_tweet_text)
        # print(tweet_text)
        # doc = nlp(tweet_text)
        age_groups = set()
        is_number_before = False
        number_before = None
        fsas = set()
        tokens = word_tokenize(tweet_text)

        for token in tokens:
            if province is None:
                if token.lower() == 'ontario':
                    province = 'ON'
                elif token.lower() == 'manitoba':
                    province = 'MB'
                elif token.lower() == 'alberta':
                    province = 'AB'
                elif token.lower() == 'quebec':
                    province = 'QB'
                elif token.lower() == 'saskatchewan':
                    province = 'SK'

            # if len(token.text) == 3 and token.text in FSA_SET:
            if len(token) == 3 and token.upper() in FSA_SET:
                fsas.add(token)
            # print(token.text)
            # if is_int(token.text[:2]):
            if is_int(token[:2]):
                # number_before = int(token.text[:2])
                number_before = int(token[:2])
                is_number_before = True
            # elif is_number_before and token.text[-1] == '+':
            elif is_number_before and token[-1] == '+':
                age_groups.add(number_before)
                is_number_before = False    
            else:
                is_number_before = False    
        

        # for ent in doc.ents:
        #     print(ent.text, ent.label_)
        #     if ent.label_ == 'GPE' and ent.text.lower() not in ('canada', 'ontario', 'alberta', 'manitoba', 'saskatchewan', 'nova scotia'):
        #         cities.add(ent.text.lower())
        #     # elif ent.label_ == 'CARDINAL':
        #     #     age_groups.add(ent.text)
        
        print("========================================")
        print("Age Groups")
        print(age_groups)

        cities = set()

        for token in tokens:
            if token.lower() in CITY_SET:
                cities.add(token.lower())
        
        if len(cities) > 0:
            cities = set([city.capitalize() for city in cities])
        if len(fsas) > 0:
            for fsa in fsas:
                cities.add(FSA_CITY_DICT[fsa][0])

        if province is None:
            for fsa in fsas:
                province = FSA_CITY_DICT[fsa][1]
                break

        print("========================================")
        print("Cities")
        print(cities)
        print()

        with Session() as session:
            province = province if province in PROVINCES else None
            cities = str(cities) if len(cities) > 0 else None
            age_groups = str(age_groups) if len(age_groups) > 0 else None
            fsas = str(fsas) if len(fsas) > 0 else None

            exists = session.query(tweets).filter_by(tweet_id=tweet_obj.id).one_or_none()
            if exists is None:
                ins = tweets.insert().values(tweet_id=tweet_obj.id,
                    tweet_text=original_tweet_text,
                    province=province,
                    age_groups=age_groups,
                    cities=cities,
                    FSAs=fsas,
                    created_at=tweet_obj.created_at,
                    )
                res = session.execute(ins)
                logger.debug(f"Inserted tweet: {tweet_obj.id}")
            else:
                session.query(tweets).filter_by(tweet_id=tweet_obj.id).update(
                    {
                        'tweet_text': original_tweet_text,
                        'province': province,
                        'age_groups': age_groups,
                        'cities': cities,
                        'FSAs': fsas,
                        'created_at': tweet_obj.created_at,
                    }
                )
                logger.debug(f"Updated tweet: {tweet_obj.id}")

            session.commit()
        
        logger.debug(f"Finished processing tweet: {tweet_obj.id} created_at: {tweet_obj.created_at}")
        # import ipdb; ipdb.set_trace()
    except Exception as e:
        logger.exception(f"Error processing tweet: {tweet_obj.id} created_at: {tweet_obj.created_at}")
