from utils import *
import tweepy
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
        if from_creator(status):
            try:
                # Prints out the tweet
                pprint(status._json)
                print(dir(status))
                print(status.text)
                process_tweet(status)
                # Saves tweet into a file
                return True
            except BaseException as e:
                print(f"Error on_status {e}")
            return True
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print("Error 420")
            #returning False in on_error disconnects the stream
            return False
