from config import *
from db import *
from listener import *
from utils import *

import datetime
from loguru import logger
import tweepy

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True)

def batch_sync():
    today = datetime.date.today()
    start_time= today - datetime.timedelta(days=3)
    logger.info(f"Starting batch syncing from {start_time} to {today}")

    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan since: {start_time} until: {today}", tweet_mode='extended', lang='en').items()
    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan", tweet_mode='extended', lang='en').items()
    count = 0
    for tweet_obj in tweets_list:
        process_tweet(tweet_obj)

batch_sync()