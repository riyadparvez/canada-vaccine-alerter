from config import *
from db import *
from listener import *
from utils import *

import datetime
import sys
import tweepy
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True, format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)
logger.add(sys.stdout, level="DEBUG", colorize=True,
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def batch_sync():
    today = datetime.date.today()
    start_time= today - datetime.timedelta(days=3)
    logger.info(f"Starting batch syncing from {start_time} to {today}")

    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan since: {start_time} until: {today}", tweet_mode='extended', lang='en').items()
    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan", tweet_mode='extended', lang='en').items()
    count = 0
    for tweet_obj in tweets_list:
        process_tweet(tweet_obj)
        count += 1
    
    logger.info(f"Synced {count} tweets")

batch_sync()
