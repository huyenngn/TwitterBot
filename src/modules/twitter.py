from io import BytesIO
import logging
import queue
import threading
import requests
import time
from requests_oauthlib import OAuth1Session
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandler:
    def __init__(self) -> None:
        self.wait_time = 5
    
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
            logger.error(f"Request returned an error: {response.status_code} {response.text}.")
            raise Exception("Exiting.")


class Client:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret) -> None:
        self.api = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        self.errors = ErrorHandler()

        response = self.api.get("https://api.twitter.com/2/users/me")

        if response.status_code != 200:
            self.errors.error_handler(response)
            return self.__init__(consumer_key, consumer_secret, access_token, access_token_secret)

        json_response = response.json()

        self.id = json_response["data"]["id"]
        self.username = json_response["data"]["username"]

    def like(self, tweet_id):
        payload = {"tweet_id": tweet_id}

        response = self.api.post(
            "https://api.twitter.com/2/users/{}/likes".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.errors.error_handler(response)
            return self.like(tweet_id)

        logger.info(f"Liked. Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            self.errors.error_handler(response)
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
            self.errors.error_handler(response)
            return self.get_tweet(tweet_id)

        return response.json()

    def create_tweet(self, params):
        if ("text" not in params.keys()) and ("media_ids" not in params.keys()):
            raise Exception("nothing to tweet...")

        payload = {}
        
        for key, value in params.items():
            k = key.split(".", 1)
            if len(k) > 1:
                if k[0] not in payload.keys():
                    payload[k[0]] = {}
                payload[k[0]][k[1]] = value
            else:
                payload[key] = value

        response = self.api.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            self.errors.error_handler(response)
            return self.create_tweet(params)

        logger.info(f"Tweeted. Response code: {response.status_code}")

        return response.json()

    def create_image(self, media):
        payload = {"media": media}

        response = self.api.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files=payload,
        )

        if response.status_code != 200:
            self.errors.error_handler(response)
            return self.create_image(media)

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
        file = BytesIO(media)

        while bytes_sent < total_bytes:
            chunk = file.read(4*1024*1024)

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
            bytes_sent = file.tell()

        logger.info("Upload chunks complete.")

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

            logger.info("Media processing status is %s " % state)

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

class StreamClient:
    def __init__(self, bearer_token) -> None:
        self.errors = ErrorHandler()
        self.bearer_token = bearer_token
        self.filtered_stream = queue.Queue()
        self.connected = queue.Queue()

    def bearer_oauth(self, r):
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r
    

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=self.bearer_oauth
        )
        if response.status_code != 200:
            self.errors.error_handler(response, self.wait_time)
            return self.get_rules()

        logger.info(f"Got rules. Response code: {response.status_code}")

        return response.json()

    def delete_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.bearer_oauth,
            json=payload,
        )
        if response.status_code != 200:
            self.errors.error_handler(response)
            return self.delete_all_rules()

        logger.info(f"Deleted rules. Response code: {response.status_code}")

    def set_rules(self, stream_rules):
        payload = {"add": stream_rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.bearer_oauth,
            json=payload,
        )

        if response.status_code != 201:
            self.errors.error_handler(response)
            return self.set_rules()

        logger.info(f"Set rules. Response code: {response.status_code}")

    def filter(self):
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/stream",
                params={
                    "expansions": "author_id,attachments.media_keys,entities.mentions.username",
                    "tweet.fields": "referenced_tweets,entities,reply_settings",
                    "media.fields": "url,type",
                    "user.fields": "username",
                },
                auth=self.bearer_oauth,
                stream=True,
            )

            if response.status_code != 200:
                self.errors.error_handler(response)
                return self.filter()

            logger.info(f"Filtered stream. Response code: {response.status_code}")
        
            for response_line in response.iter_lines():
                if response_line:
                    json_response = json.loads(response_line)
                    logger.info(json.dumps(json_response, indent=4, sort_keys=True))
                    if "errors" in json_response:
                        self.connected.put_nowait(False)
                        break
                    self.connected.put_nowait(True)
                    self.filtered_stream.put_nowait(json_response)


    def get_filter(self):
            t_stream = threading.Thread(target=self.filter)
            t_stream.start()
            while self.connected.get():
                yield self.filtered_stream.get()
            t_stream.join()

