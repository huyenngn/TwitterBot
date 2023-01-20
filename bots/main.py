import time
from requests_oauthlib import OAuth1Session
import os
import requests
import json
from googletrans import Translator
import logging
import threading

DEBUG = True

FREEN_TWT = "srchafreen"
BECKY_TWT = "AngelssBecky"

FREEN_EMOJI = "\ud83d\udc30"
BECKY_EMOJI = "\ud83e\uddda\ud83c\udffb\u200d\u2640\ufe0f"

if DEBUG:
    stream_rules = [
    {"value": 'from:joohwangblink -is:retweet', "tag": "debug"}
    ]
else:
    stream_rules = [
    {"value": 'to:'+FREEN_TWT+' is:verified', "tag": "freen_reply"},
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

wait_time = 5

def backoff(response):
    if (response.status_code >= 400) and (response.status_code < 420):
        logger.error(f"Request returned an error: {response.status_code} {response.text}.")
        raise Exception("Exiting.")
    elif (response.status_code >= 420) and (response.status_code <= 429):
        limit = int(response.headers['x-rate-limit-reset']) - time.time() + 5
        logger.error(f"Error (HTTP {response.status_code}): {response.text}. Reconnecting in {limit} seconds.")
        saved = time.time()
        while (time.time() - saved) < limit:
            time.sleep(1)
    else:
        wait_time = min(wait_time, 320)
        logger.error(f"Network error (HTTP {response.status_code}): {response.text}. Reconnecting {wait_time}.")
        saved = time.time()
        while (time.time() - saved) < wait_time:
            time.sleep(1)
        wait_time *= 2


class Client:
    def __init__(self):
        self.api = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
        )
        self.id = "1601180254931980288"

        logger.info("Set up client.")

    def like(self, tweet_id):
        payload = {"tweet_id": tweet_id}

        response = self.api.post(
            "https://api.twitter.com/2/users/{}/likes".format(self.id), json=payload
        )

        if response.status_code != 200:
            backoff(response)
            self.like()
        
        logger.info(f"Liked. Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            backoff(response)
            self.retweet()
        
        logger.info(f"Retweeted. Response code: {response.status_code}")

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
            backoff(response)
            self.create_tweet(kwargs)

        logger.info(f"Tweeted. Response code: {response.status_code}")

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
        )
        if response.status_code != 200:
            backoff(response)
            self.get_rules()

        logger.info(f"Got rules. Response code: {response.status_code}")

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
            backoff(response)
            self.delete_all_rules()

        logger.info(f"Deleted rules. Response code: {response.status_code}")
            
        print(json.dumps(response.json()))

    def set_rules(self):
        payload = {"add": stream_rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=bearer_oauth,
            json=payload,
        )
        if response.status_code != 201:
            backoff(response)
            self.set_rules()

        logger.info(f"Set rules. Response code: {response.status_code}")

        print(json.dumps(response.json()))


class TranslationAnswer(Client):
    def __init__(self):
        self.trans = Translator()
        self.last_response_time = None

        super(TranslationAnswer, self).__init__()

    def get_stream(self):
        self.delete_all_rules()
        self.set_rules()
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            params={"expansions": "author_id"},
            auth=bearer_oauth,
            stream=True
        )

        logger.info(f"Filtered stream. Response code: {response.status_code}")
        print(response.headers)
        if response.status_code != 200:
            backoff(response)
            self.get_stream()
        
        for response_line in response.iter_lines():
            logger.info("Recieved content or heartbeat.")
            self.last_response_time = time.time()
            if response_line:                
                json_response = json.loads(response_line)

                if json_response["matching_rules"][0]["tag"] == "freen":
                    translation = FREEN_EMOJI + ": "
                elif json_response["matching_rules"][0]["tag"] == "becky":
                    translation = BECKY_EMOJI + ": "
                else:
                    translation = "[en] "
                translation += self.trans.translate(json_response["data"]["text"], src='th', dst='en').text

                tweet_id = json_response["data"]["id"]

                self.create_tweet(text=translation, in_reply_to_tweet_id=tweet_id)
                self.like(tweet_id)
                self.retweet(tweet_id)

                print(json.dumps(json_response, indent=4, sort_keys=True))
            
def main():
    ta = TranslationAnswer()
    t_stream = threading.Thread(target=ta.get_stream)
    t_stream.start()
    while True:
        passed = time.time() - ta.last_response_time
        logger.info(f"Time passed with no heartbeat: {passed}")
        if (ta.last_response_time is not None) and (passed > 20):
            logger.info("About to disconnect.")
            t_stream.join()
            logger.info("Disconnected.")
            t_stream = threading.Thread(target=ta.get_stream)
            t_stream.start()
        time.sleep(10)
    

if __name__ == "__main__":
    main()