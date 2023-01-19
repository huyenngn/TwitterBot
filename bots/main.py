import time
import tweepy
import os
import logging
from googletrans import Translator
import requests

DEBUG = True

FREEN_TWT = "srchafreen"
BECKY_TWT = "AngelssBecky"

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

if DEBUG:
    rules = [
    tweepy.StreamRule('from:joohwangblink -is:retweet', tag='debug'),
    ]
else:
    rules = [
    tweepy.StreamRule('to:'+FREEN_TWT+' is:verified!', tag='freen_reply'),
    tweepy.StreamRule('to:'+BECKY_TWT+' is:verified', tag='becky_reply'),
    tweepy.StreamRule('from:'+FREEN_TWT+' -is:retweet', tag='freen'),
    tweepy.StreamRule('from:'+BECKY_TWT+' -is:retweet', tag='becky')
    ]

api = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token = bearer_token,
    wait_on_rate_limit=True
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

trans = Translator()

saved = time.perf_counter()

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    return r

params = {"x-rate-limit-remaining": "search"}
    
response = requests.get("https://api.twitter.com/2/tweets/search/recent", params=params, auth=bearer_oauth)


class TranslationAnswer(tweepy.StreamingClient):
    def on_connect(self):
        saved = time.perf_counter()

        rule_ids = []
        response = self.get_rules()
        for rule in response.data:
            rule_ids.append(rule.id)

        if(len(rule_ids) > 0):
            self.delete_rules(rule_ids)

        self.add_rules(rules)
        logger.info("added rules")
        
        response = self.get_rules()
        for rule in response.data:
            logger.info(f"{rule}")
        
    def on_tweet(self, tweet):
        saved = time.perf_counter()

        result = api.get_user(id=tweet.author_id).data.username + ": "
        if result == FREEN_TWT:
            result = "F: "
        elif result == BECKY_TWT:
            result = "B: "
        result += trans.translate((tweet.text), src='th', dst='en').text
        logger.info(f"got tweet... {tweet.id, tweet.text, result, tweet.author_id}")
        api.create_tweet(text=result, in_reply_to_tweet_id=tweet.id)
        api.like(tweet.id)
        api.retweet(tweet.id)

    def on_errors(self, errors):
        logger.error(errors)
    
    def on_keep_alive(self):
        self.disconnect()
        main()

    def on_exception(self, exception):
        logger.exception(exception)
        main()

def main():
    ta = TranslationAnswer(bearer_token=bearer_token, wait_on_rate_limit=True, max_retries = 20)
    ta.filter(expansions=["author_id"])
    logger.info(response.headers)

if __name__ == "__main__":
    main()
