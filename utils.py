from db import *

import emoji
import nltk
import pickle
import re
# import spacy
from nltk.tokenize import word_tokenize

# nlp = spacy.load("en_core_web_trf")
PROVINCES = ('AB', 'ON', 'MB', 'BC', 'QC', 'SK')

with open('FSA.pickle', 'rb') as handle:
    FSA_SET = pickle.load(handle)

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
    # place = tweet_obj._json["place"]
    # entities = tweet_obj._json["entities"]

    tweet_url = f"https://twitter.com/twitter/statuses/"

    if "full_text" in tweet_obj._json:
        original_tweet_text = tweet_obj._json["full_text"]
    elif "full_text" in tweet_obj._json['extended_tweet']:
        original_tweet_text = tweet_obj._json['extended_tweet']["full_text"]
    
    province = original_tweet_text[:4][1:-1]
    tweet = original_tweet_text[5:]
    print(tweet)
    age_groups = re.match(r'^([\s\d]+)+$', original_tweet_text)
    # print(age_groups)

    print()
    print()

    tweet_text = cleaner(original_tweet_text)
    # print(tweet_text)
    # doc = nlp(tweet_text)
    age_groups = set()
    is_number_before = False
    number_before = None
    fsas = set()

    for token in word_tokenize(tweet_text):
        # if len(token.text) == 3 and token.text in FSA_SET:
        if len(token) == 3 and token in FSA_SET:
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
            print(number_before)
        else:
            is_number_before = False    
    print("========================================")
    print("Age Groups")
    print(age_groups)

    print("========================================")
    print("Entities")
    cities = set()
    # for ent in doc.ents:
    #     print(ent.text, ent.label_)
    #     if ent.label_ == 'GPE' and ent.text.lower() not in ('canada', 'ontario', 'alberta', 'manitoba', 'saskatchewan', 'nova scotia'):
    #         cities.add(ent.text.lower())
    #     # elif ent.label_ == 'CARDINAL':
    #     #     age_groups.add(ent.text)
    
    print(cities)
    print()

    with engine.connect() as connection:
        province = province if province in PROVINCES else None
        cities = str(cities) if cities in cities else None
        age_groups = str(age_groups) if len(age_groups) > 0 else None
        fsas = str(fsas) if len(fsas) > 0 else None

        ins = tweets.insert().values(tweet_id=tweet_obj.id,
            tweet_text=original_tweet_text,
            province=province,
            age_groups=age_groups,
            cities=cities,
            FSAs=fsas,
            created_at=tweet_obj.created_at,
            )
        res = connection.execute(ins)
        # print(res)

    # break
    # import ipdb; ipdb.set_trace()
