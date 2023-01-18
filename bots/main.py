import time
import tweepy
import os
import logging
from googletrans import Translator

FREEN_TWT = "srchafreen"
BECKY_TWT = "AngelssBecky"

rules = [
    # tweepy.StreamRule('from:joohwangblink -is:retweet', tag='debug'),
    tweepy.StreamRule('to:'+FREEN_TWT+' is:verified!', tag='freen_reply'),
    tweepy.StreamRule('to:'+BECKY_TWT+' is:verified', tag='becky_reply'),
    tweepy.StreamRule('from:'+FREEN_TWT+' -is:retweet', tag='freen'),
    tweepy.StreamRule('from:'+BECKY_TWT+' -is:retweet', tag='becky')
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

api = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token = bearer_token,
    wait_on_rate_limit=True
)

trans = Translator()

saved = time.perf_counter()


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

    def on_closed(self, response):
        logger.error(f"closed by twt.... {response}")
        time.sleep(300)

    def on_request_error(self, status_code):
        logger.error(f"request error.... {status_code}")
        time.sleep(300)


def main():
    ta = TranslationAnswer(bearer_token=bearer_token, wait_on_rate_limit=True)
    ta.filter(expansions=["author_id"], threaded=True)
    while (time.perf_counter() - saved) < 90:
        continue
    ta.disconnect()

if __name__ == "__main__":
    while True:
        main()