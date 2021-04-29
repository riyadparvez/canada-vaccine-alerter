from config import *
from db import *
from listener import *
from utils import *

import datetime
from sqlalchemy import text as sa_text
import tweepy

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True)

def f():
    today = datetime.date.today()
    yesterday= today - datetime.timedelta(days=2)

    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan since: {yesterday} until: {today}", tweet_mode='extended', lang='en').items()
    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan", tweet_mode='extended', lang='en').items()
    output = []
    for tweet_obj in tweets_list:
        process_tweet(tweet_obj)

f()
