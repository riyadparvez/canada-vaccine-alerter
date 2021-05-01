from config import *
from listener import *

import datetime
import tweepy
from loguru import logger

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
        stream.filter(follow=["1373531468744552448"])
    except Exception as e:
        logger.exception(f"Stream exited")

