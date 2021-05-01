from utils import *
import tweepy
from loguru import logger
from pprint import pprint

def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    else:
        return True

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            if from_creator(status):
                # Prints out the tweet
                pprint(status._json)
                print(status.text)
                process_tweet(status)
                # Saves tweet into a file
                return True
        except BaseException as e:
            logger.exception(f"Error on_status {status}")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print("Error 420")
            #returning False in on_error disconnects the stream
            return False
