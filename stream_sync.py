from config import *
from listener import *

import tweepy
import datetime

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True)

def f():
    today = datetime.date.today()
    yesterday= today - datetime.timedelta(days=1)

    tweets_list = tweepy.Cursor(api.search, q="from:vaxhunterscan since:" + str(yesterday)+ " until:" + str(today),tweet_mode='extended', lang='en').items()

    output = []
    for tweet in tweets_list:
        text = tweet._json["full_text"]
        print(text)
        favourite_count = tweet.favorite_count
        retweet_count = tweet.retweet_count
        created_at = tweet.created_at
        
        line = {'text' : text, 'favourite_count' : favourite_count, 'retweet_count' : retweet_count, 'created_at' : created_at}
        output.append(line)

listener = MyStreamListener()

# stream = tweepy.Stream(
#   TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
#   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, listener=MyStreamListener()
# )

stream = tweepy.Stream(auth = api.auth, listener=MyStreamListener())
# stream.filter(track=["Tweepy"])
stream.filter(follow=["1373531468744552448"])
