import logging
import requests
import time
from requests_oauthlib import OAuth1Session
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


class Twitter:
    def __init__(self, api=None):
        if api is None:
            self.api = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret,
            )
        else:
            self.api = api

        self.wait_time = 5

        response = self.api.get("https://api.twitter.com/2/users/me")

        if response.status_code != 200:
            self.error_handler(response)
            self.__init__(api=api)

        json_response = response.json()

        self.id = json_response["data"]["id"]
        self.username = json_response["data"]["username"]

        logger.info(f"Set user data. Response code: {response.status_code}")

    def error_handler(self, response):
        logger.info(json.dumps(response.json()))

        if response.status_code > 429:
            self.wait_time = min(self.wait_time, 320)
            logger.error(
                f"Network error (HTTP {response.status_code}): {response.text}. Reconnecting {self.wait_time}."
            )
            saved = time.time()
            while (time.time() - saved) < self.wait_time:
                time.sleep(1)
            self.wait_time *= 2
        elif response.status_code >= 420:
            limit = int(response.headers["x-rate-limit-reset"]) - time.time() + 5
            logger.error(
                f"Error (HTTP {response.status_code}): {response.text}. Reconnecting in {limit} seconds."
            )
            saved = time.time()
            while (time.time() - saved) < limit:
                time.sleep(1)
        else:
            logger.error(
                f"Request returned an error: {response.status_code} {response.text}."
            )
            raise Exception("Exiting.")

    def get_api(self):
        return self.api

    def like(self, tweet_id):
        payload = {"tweet_id": tweet_id}

        response = self.api.post(
            "https://api.twitter.com/2/users/{}/likes".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.error_handler(response)
            return self.like(tweet_id)

        logger.info(f"Liked. Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.error_handler(response)
            return self.retweet(tweet_id)

        logger.info(f"Retweeted. Response code: {response.status_code}")

    def get_tweet(self, tweet_id):
        response = self.api.get(
            "https://api.twitter.com/2/tweets/{}".format(tweet_id),
            params={
                "expansions": "author_id,attachments.media_keys,entities.mentions.username",
                "tweet.fields": "referenced_tweets,entities,reply_settings",
                "media.fields": "url,type",
                "user.fields": "username",
            },
        )

        if response.status_code != 200:
            self.error_handler(response)
            return self.get_tweet(tweet_id)

        return response.json()

    def create_media(self, media):
        payload = {"media": media}

        response = self.api.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files=payload,
        )

        if response.status_code != 200:
            self.error_handler(response)
            return self.create_media(media)

        return response.json()

    def create_video(self, media):
        total_bytes = len(media)
        request_data = {
            "command": "INIT",
            "media_type": "video/mp4",
            "total_bytes": total_bytes,
            "media_category": "tweet_video",
        }

        req = requests.post(
            url="https://upload.twitter.com/1.1/media/upload.json",
            data=request_data,
            auth=self.api,
        )

        media_id = req.json()["media_id"]

        segment_id = 0
        bytes_sent = 0

        while bytes_sent < total_bytes:
            chunk = media[bytes_sent:(4 * 1024 * 1024)]

            print("APPEND")

            request_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment_id,
            }

            files = {"media": chunk}

            req = requests.post(
                url="https://upload.twitter.com/1.1/media/upload.json",
                data=request_data,
                files=files,
                auth=self.api,
            )

            if req.status_code < 200 or req.status_code > 299:
                print(req.status_code)
                print(req.text)
                return ""

            segment_id = segment_id + 1
            bytes_sent += 4 * 1024 * 1024

        print("Upload chunks complete.")

        request_data = {"command": "FINALIZE", "media_id": media_id}

        req = requests.post(
            url="https://upload.twitter.com/1.1/media/upload.json",
            data=request_data,
            auth=self.api,
        )

        while True:
            processing_info = req.json().get("processing_info", None)

            if processing_info is None:
                return media_id

            state = processing_info["state"]

            print("Media processing status is %s " % state)

            if state == "succeeded":
                return media_id

            if state == "failed":
                return ""

            check_after_secs = processing_info["check_after_secs"]

            time.sleep(check_after_secs)

            request_params = {"command": "STATUS", "media_id": media_id}

            req = requests.get(
                url="https://upload.twitter.com/1.1/media/upload.json",
                params=request_params,
                auth=self.api,
            )

    def create_tweet(self, **kwargs):
        if ("text" not in kwargs) and ("media_ids" not in kwargs):
            raise Exception("nothing to tweet...")

        payload = {}
        reply = ["in_reply_to_tweet_id"]
        media = ["media_ids"]
        for key, value in kwargs.items():
            if key in reply:
                if "reply" not in payload.keys():
                    payload["reply"] = {}
                payload["reply"][key] = value
            elif key in media:
                if value:
                    if "media" not in payload.keys():
                        payload["media"] = {}
                    payload["media"][key] = value
            else:
                payload[key] = value

        response = self.api.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            self.error_handler(response)
            return self.create_tweet(kwargs)

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
            json=payload,
        )
        if response.status_code != 200:
            self.error_handler(response)
            return self.delete_all_rules()

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
            self.error_handler(response)
            return self.set_rules()

        logger.info(f"Set rules. Response code: {response.status_code}")

        logger.info(json.dumps(response.json()))

    def get_stream(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            params={
                "expansions": "author_id,attachments.media_keys,entities.mentions.username",
                "tweet.fields": "referenced_tweets,entities,reply_settings",
                "media.fields": "url,type",
                "user.fields": "username",
            },
            auth=bearer_oauth,
            stream=True,
        )

        if response.status_code != 200:
            self.error_handler(response)
            return self.get_stream()

        logger.info(f"Filtered stream. Response code: {response.status_code}")

        return response
