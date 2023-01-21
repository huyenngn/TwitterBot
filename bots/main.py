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
STRANGER_EMOJI = "\ud83d\udc64"

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

WAIT_TIME = 5


def backoff(response):
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
        WAIT_TIME = min(WAIT_TIME, 320)
        logger.error(
            f"Network error (HTTP {response.status_code}): {response.text}. Reconnecting {WAIT_TIME}.")
        saved = time.time()
        while (time.time() - saved) < WAIT_TIME:
            time.sleep(1)
        WAIT_TIME *= 2
    WAIT_TIME = 5


class Twitter:
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
            self.like(tweet_id)

        logger.info(f"Liked. Response code: {response.status_code}")

    def retweet(self, tweet_id):
        payload = {"tweet_id": tweet_id}
        response = self.api.post(
            "https://api.twitter.com/2/users/{}/retweets".format(self.id), json=payload
        )

        if response.status_code != 200:
            backoff(response)
            self.retweet(tweet_id)

        logger.info(f"Retweeted. Response code: {response.status_code}")

    def get_tweet(self, tweet_id):
        response = self.api.get(
            "https://api.twitter.com/2/tweets",
            params={
                "ids": tweet_id,
                "expansions": "author_id",
                "tweet.fields": "referenced_tweets"
            }
        )

        if response.status_code != 200:
            backoff(response)
            self.get_tweet(tweet_id)

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
            backoff(response)
            self.delete_all_rules()

        logger.info(f"Deleted rules. Response code: {response.status_code}")

        logger.info(json.dumps(response.json()))

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

        logger.info(json.dumps(response.json()))

    def get_stream(self):
        self.delete_all_rules()
        self.set_rules()
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            params={"expansions": "author_id,attachments.media_keys",
                    "tweet.fields": "referenced_tweets",
                    "media.fields": "url"},
            auth=bearer_oauth,
            stream=True
        )

        logger.info(f"Filtered stream. Response code: {response.status_code}")

        if response.status_code != 200:
            backoff(response)
            self.get_stream()

        self.last_response_time = time.time()

        return response


class Twitter_Interacter(Twitter):
    def __init__(self):
        self.trans = Translator()
        self.last_response_time = None

        super(Twitter_Interacter, self).__init__()

    def interact(self):
        response = self.get_stream()

        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response,
                            indent=4, sort_keys=True))
                
                if json_response["matching_rules"][0]["tag"] == "freen":
                    translation = FREEN_EMOJI + ": "
                elif json_response["matching_rules"][0]["tag"] == "becky":
                    translation = BECKY_EMOJI + ": "
                else:
                    translation = STRANGER_EMOJI + ": "

                has_quote = ("referenced_tweets" in json_response["data"]) and (
                    json_response["data"]["referenced_tweets"][0]["type"] == "quoted")
                has_media = "media" in json_response["includes"]
                is_reply = ("referenced_tweets" in json_response["data"]) and (
                    json_response["data"]["referenced_tweets"][0]["type"] == "replied_to")

                # TODO: remove mention when its a reply remove tweet_links and media_links at end of tweet
                text = json_response["data"]["text"]

                if is_reply:
                    text = (text.split('@', 1)[-1]).split(' ', 1)[-1]
                if has_quote:
                    text = text.rsplit(' ', 1)[0]
                translation += self.trans.translate(text,
                                                    src='th', dst='en').text

                tweet_id = json_response["data"]["id"]

                self.create_tweet(text=translation,
                                  in_reply_to_tweet_id=tweet_id)
                self.like(tweet_id)

                if has_media:
                    temp = translation.split('https://')
                    for i in range(1, len(temp)):
                        temp1 = temp[i].split(' ', 1)
                        temp[i] = temp1[-1] if (len(temp1) > 1) else ""
                    translation = ''.join(temp)

                if translation != "":
                    self.create_tweet(text=translation, quote_tweet_id=tweet_id)

def main():
    ti = Twitter_Interacter()
    t_stream = threading.Thread(target=ti.interact)
    t_stream.start()
    while True:
        if (ti.last_response_time is not None) and ((time.time() - ti.last_response_time) > 30):
            logger.info("About to disconnect.")
            t_stream.join()
            logger.info("Disconnected.")
            t_stream = threading.Thread(target=ti.get_stream)
            t_stream.start()
        time.sleep(10)


if __name__ == "__main__":
    main()
