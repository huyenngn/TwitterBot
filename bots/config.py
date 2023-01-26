import os
import requests
import time
from requests_oauthlib import OAuth1Session
import json
import base64
from helpers import logger
import threading

from twitter import Twitter_Interacter
from instagram import Instagram_Reposter

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

def error_handler(response, wait_time):
    if (response.status_code >= 400) and (response.status_code < 420):
        logger.error(
            f"Request returned an error: {response.status_code} {response.text}.")
        raise Exception("Exiting.")
    elif (response.status_code >= 420) and (response.status_code <= 429):
        limit = int(response.headers['x-rate-limit-reset']) - time.time() + 5
        logger.error(
            f"Error (HTTP {response.status_code}): {response.text}. Reconnecting in {limit} seconds.")
        saved = time.time()
        while (time.time() - saved) < limit:
            time.sleep(1)
    else:
        wait_time = min(wait_time, 320)
        logger.error(
            f"Network error (HTTP {response.status_code}): {response.text}. Reconnecting {wait_time}.")
        saved = time.time()
        while (time.time() - saved) < wait_time:
            time.sleep(1)
        wait_time *= 2

class API:
    def __init__(self):
        self.api = None
        self.id = "1601180254931980288"
        self.wait_time = 5

        logger.info("Set up client.")
    
    def get_api(self):
        if self.api == None:
            self.api = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
            )

        return self.api
    def set_api(self, api):
        self.api = api

    def like(self, tweet_id):
        payload = {"tweet_id": tweet_id}

        response = self.api.post(
            "https://api.twitter.com/2/users/{}/likes".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            self.like(tweet_id)

        logger.info(f"Liked. Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            self.retweet(tweet_id)

        logger.info(f"Retweeted. Response code: {response.status_code}")

    def get_tweet(self, tweet_id):
        response = self.api.get(
            "https://api.twitter.com/2/tweets/{}".format(tweet_id),
            params={
                "expansions": "author_id,attachments.media_keys",
                "tweet.fields": "referenced_tweets,entities",
                "media.fields": "url",
                "user.fields": "username"}
        )

        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            return self.get_tweet(tweet_id)

        return response.json()
    
    def post_media(self, media):
        encoded_string = base64.b64encode(media.read())

        payload = {"media_data": encoded_string}

        response = self.api.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            json=payload,
        )

        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            return self.post_media(media)
        
        return response.json()

    def create_tweet(self, **kwargs):
        if ('text' not in kwargs) and ('media_ids' not in kwargs):
            raise Exception("nothing to tweet...")
        
        payload = {}
        reply = ["in_reply_to_tweet_id"]
        media = ["media_ids"]
        for key, value in kwargs.items():
            if key in reply:
                payload["reply"] = {key: value}
            elif key in media:
                payload["media"] = {key: value}
            else:
                payload[key] = value

        response = self.api.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            self.error_handler(response, self.wait_time)
            self.create_tweet(kwargs)

        logger.info(f"Tweeted. Response code: {response.status_code}")

        return response.json()

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
        )
        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            return self.get_rules()

        logger.info(f"Got rules. Response code: {response.status_code}")

        logger.info(json.dumps(response.json()))
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
            self.error_handler(response, self.wait_time)
            self.delete_all_rules()

        logger.info(f"Deleted rules. Response code: {response.status_code}")

        logger.info(json.dumps(response.json()))

    def set_rules(self, stream_rules):
        payload = {"add": stream_rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=bearer_oauth,
            json=payload,
        )
        if response.status_code != 201:
            self.error_handler(response, self.wait_time)
            self.set_rules()

        logger.info(f"Set rules. Response code: {response.status_code}")

        logger.info(json.dumps(response.json()))

    def get_stream(self, stream_rules):
        self.delete_all_rules()
        self.set_rules(stream_rules)
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            params={"expansions": "author_id,attachments.media_keys",
                    "tweet.fields": "referenced_tweets",
                    "media.fields": "url",
                    "user.fields": "username"},
            auth=bearer_oauth,
            stream=True
        )

        logger.info(f"Filtered stream. Response code: {response.status_code}")

        if response.status_code != 200:
            self.error_handler(response, self.wait_time)
            return self.get_stream()

        return response

def main():
    ti = Twitter_Interacter()
    api = ti.get_api()
    t_twitter = threading.Thread(target=ti.start)
    t_twitter.start()
    ir = Instagram_Reposter()
    ir.set_api(api)
    t_insta = threading.Thread(target=ir.start)
    t_insta.start()

if __name__ == "__main__":
    main()