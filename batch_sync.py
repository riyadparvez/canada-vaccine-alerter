from config import *
from db import *
from listener import *
from utils import *

import argparse
import datetime
import sys
import tweepy
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True,
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Pipeline Orchestrator")
    parser.add_argument(
        "-d",
        "--days-to-sync",
        type=int,
        required=False,
        default=1,
        help="Days to sync.",
    )
    return parser.parse_args()


def batch_sync(days_to_sync):
    today = datetime.date.today()
    start_time= today - datetime.timedelta(days=days_to_sync)
    logger.info(f"Starting batch syncing from {start_time} to {today}")

    # tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan since: {start_time} until: {today} exclude:replies", tweet_mode='extended', lang='en').items()
    tweets_list = tweepy.Cursor(api.search, q=f"from:vaxhunterscan since: {start_time} until: {today}", tweet_mode='extended', lang='en').items()
    count = 0
    for tweet_obj in tweets_list:
        process_tweet(tweet_obj)
        count += 1
    
    logger.info(f"Synced {count} tweets")


if __name__ == '__main__':
    args = parse_arguments()
    batch_sync(args.days_to_sync)
