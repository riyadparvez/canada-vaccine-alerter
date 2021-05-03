from config import *
from db import *
from listener import *
from utils import *

import argparse
import datetime
import sys
import time
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


def limit_handled(cursor):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            logger.error(f"Rate Limit is reached. Sleeping for 15 minutes.")
            time.sleep(15 * 60)


def batch_sync(days_to_sync: int):
    today = datetime.date.today()
    start_time= today - datetime.timedelta(days=days_to_sync)
    logger.info(f"Starting batch syncing from {start_time} to {today}")

    search_query = f"from:vaxhunterscan since: {start_time} until: {today} exclude:replies"
    search_query = f"from:vaxhunterscan since: {start_time} until: {today}"
    search_query = f"from:vaxhunterscan since: {start_time}"
    search_query = f"from:vaxhunterscan"
    cursor = tweepy.Cursor(api.search, q=search_query, tweet_mode='extended', lang='en')
    tweets = []
    # for tweet_obj in limit_handled(cursor.items()):
    for tweet_obj in cursor.items(200):
        process_tweet(tweet_obj)
        tweets.append(tweet_obj)

    logger.info(f"Finished syncing {len(tweets)} tweets")


if __name__ == '__main__':
    args = parse_arguments()
    batch_sync(args.days_to_sync)
