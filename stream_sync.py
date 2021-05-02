from config import *
from listener import *

import sys
import tweepy
from loguru import logger

VAX_HUNTER_TWITTER_ID = "1373531468744552448"

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True, format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True)

listener = MyStreamListener()

# stream = tweepy.Stream(
#   TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
#   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, listener=MyStreamListener()
# )

stream = tweepy.Stream(auth = api.auth, listener=MyStreamListener())
# stream.filter(track=["Tweepy"])

while True:
    try:
        logger.info("Starting sync from Twitter stream")
        stream.filter(follow=[VAX_HUNTER_TWITTER_ID])
    except Exception as e:
        logger.exception(f"Stream exited")

