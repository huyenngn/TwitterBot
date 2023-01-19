from requests_oauthlib import OAuth1Session
import os
import requests
import json
from googletrans import Translator
import logging

DEBUG = True

FREEN_TWT = "srchafreen"
BECKY_TWT = "AngelssBecky"

if DEBUG:
    rules = [
    {"value": 'from:joohwangblink -is:retweet', "tag": "debug"}
    ]
else:
    rules = [
    {"value": 'to:'+FREEN_TWT+' is:verified!', "tag": "freen_reply"},
    {"value": 'to:'+BECKY_TWT+' is:verified', "tag": "becky_reply"},
    {"value": 'from:'+FREEN_TWT+' -is:retweet', "tag": "freen"},
    {"value": 'from:'+BECKY_TWT+' -is:retweet', "tag": "becky"}
    ]

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class Client:
    def __init__(self):
        self.api = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
        )
        self.trans = Translator()
        self.id = 1601180254931980288

    def like(self, tweet_id):
        payload = {"tweet_id": tweet_id}

        response = self.api.post(
            "https://api.twitter.com/2/users/{}/likes".format(self.id), json=payload
        )

        if response.status_code != 200:
            logger.error(f"Request returned an error: {response.status_code} {response.text}")

        logger.info(f"Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            logger.error(f"Request returned an error: {response.status_code} {response.text}")

        logger.info(f"Response code: {response.status_code}")

    def create_tweet(self, **kwargs):
        if ('text' not in kwargs) and ('media_ids' not in kwargs):
            raise Exception("nothing to tweet...")
        
        payload = {}
        reply = ["in_reply_to_tweet_id"]
        media = ["media_ids"]
        for key, value in kwargs.items():
            if key in reply:
                payload["reply"]={key : value}
            elif key in media:
                payload["media"]={key : value}
            else:
                payload[key]=value

        response = self.api.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            logger.error(f"Request returned an error: {response.status_code} {response.text}")

        logger.info(f"Response code: {response.status_code}")

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
        )
        if response.status_code != 200:
            logger.error(f"Cannot get rules (HTTP {response.status_code}): {response.text}")
        print(json.dumps(response.json()))
        return response.json()

    def delete_all_rules(self):
        rules = self.get_rules()

        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=bearer_oauth,
            json=payload
        )
        if response.status_code != 200:
            logger.error(f"Cannot delete rules (HTTP {response.status_code}): {response.text}")
        print(json.dumps(response.json()))

    def set_rules(self):
        payload = {"add": rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=bearer_oauth,
            json=payload,
        )
        if response.status_code != 201:
            logger.error(f"Cannot add rules (HTTP {response.status_code}): {response.text}")
        print(json.dumps(response.json()))

    def get_stream(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            params={"expansions": "author_id"},
            auth=bearer_oauth, 
            stream=True
        )

        print(response.status_code)
        if response.status_code != 200:
            limit = response.headers['x-rate-limit-remaining']
            logger.error(f"Cannot get stream (HTTP {response.status_code}): {response.text}... {limit} seconds")
        
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                tweet_id = json_response["data"]["id"]
                translation = self.trans.translate(json_response["data"]["text"], src='th', dst='en').text
                self.create_tweet(text=translation, in_reply_to_tweet_id=tweet_id)
                self.like(tweet_id)
                self.retweet(tweet_id)
                print(json.dumps(json_response, indent=4, sort_keys=True))

def main():
    ta = Client()
    ta.delete_all_rules()
    ta.set_rules()
    ta.get_stream()


if __name__ == "__main__":
    main()