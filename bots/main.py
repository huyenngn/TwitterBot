import tweepy
import os
from googletrans import Translator

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

translator = Translator()

sclient = tweepy.StreamingClient(bearer_token=bearer_token, wait_on_rate_limit=True)
rules = [
    tweepy.StreamRule('from:srchafreen -is:retweet', tag='freen'),
    tweepy.StreamRule('from:joohwangblink -is:retweet', tag='sofia'),
    tweepy.StreamRule('from:AngelssBecky -is:retweet', tag='becky')
]
sclient.add_rules(rules)

response = sclient.get_rules()
for rule in response.data:
    print(rule)

class TranslationAnswer(tweepy.StreamingClient):

    def on_tweet(self, tweet):
        result = "[EN] "
        result += translator.translate(tweet.text, src='th', dst='en').text
        print(tweet.id, tweet.text, result, tweet.author_id)
        client.create_tweet(text=result, in_reply_to_tweet_id=tweet.id)
        client.like(tweet.id)
        client.retweet(tweet.id)

    def on_errors(self, errors):
        print(errors)

    def on_connection_error(self):
        self.disconnect()


ta = TranslationAnswer(bearer_token=bearer_token, wait_on_rate_limit=True)
ta.filter()
