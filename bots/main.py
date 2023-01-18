import tweepy
import os
import logging
from googletrans import Translator

rules = [
    tweepy.StreamRule('from:srchafreen -is:retweet', tag='freen'),
    tweepy.StreamRule('from:joohwangblink -is:retweet', tag='sofia'),
    tweepy.StreamRule('from:AngelssBecky -is:retweet', tag='becky')
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
    access_token_secret=access_token_secret
)

trans = Translator()

class TranslationAnswer(tweepy.StreamingClient):
    def on_connect(self):
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
        result = "[EN] "
        result += trans.translate((tweet.text), src='th', dst='en').text
        logger.info(f"got tweet... {tweet.id, tweet.text, result, tweet.author_id}")
        api.create_tweet(text=result, in_reply_to_tweet_id=tweet.id)
        api.like(tweet.id)
        api.retweet(tweet.id)

    def on_errors(self, errors):
        logger.error(errors)

    def on_connection_error(self):
        self.disconnect()

def main():
    ta = TranslationAnswer(bearer_token=bearer_token, wait_on_rate_limit=True)
    ta.filter()

if __name__ == "__main__":
    main()