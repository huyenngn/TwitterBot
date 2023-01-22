import time
from requests_oauthlib import OAuth1Session
import os
import requests
import json
from googletrans import Translator
import logging
import threading

DEBUG = True

twitter_handles = {
    "freen": "srchafreen",
    "becky": "AngelssBecky",
    "nam": "namorntaraaa",
    "gap": "GAPtheseries"
}

emojis = {
    "freen":  "\ud83d\udc30",
    "becky": "\ud83e\uddda\ud83c\udffb\u200d\u2640\ufe0f",
    "nam": "\ud83d\udea2",
    "gap": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
    "other": "\ud83d\udc64"
}


if DEBUG:
    stream_rules = [
        {"value": 'from:joohwangblink -is:retweet', "tag": "other"}
    ]
else:
    stream_rules = [
        {"value": 'from:'+twitter_handles["freen"]+' -is:retweet', "tag": "freen"},
        {"value": 'from:'+twitter_handles["becky"]+' -is:retweet', "tag": "becky"}
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
                "expansions": "author_id,attachments.media_keys",
                "tweet.fields": "referenced_tweets",
                "media.fields": "url",
                "user.fields": "username"}
        )

        if response.status_code != 200:
            backoff(response)
            return self.get_tweet(tweet_id)

        return response

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
            return self.get_stream()

        return response


class Twitter_Interacter(Twitter):
    def __init__(self):
        self.trans = Translator()
        self.last_response_time = None

        super(Twitter_Interacter, self).__init__()

    def translate_tweet(self, data, json_response, tag):
        is_quote = ("referenced_tweets" in data) and (
            data["referenced_tweets"][0]["type"] == "quoted")
        is_reply = ("referenced_tweets" in data) and (
            data["referenced_tweets"][0]["type"] == "replied_to")
        has_media = "media" in json_response["includes"]

        text = data["text"]

        if is_quote:
            text = text.rsplit(' ', 1)[0]
        if is_reply:
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split('@', reply_number)[-1].split(' ', 1)
            text = mentions[-1] if len(mentions) > 1 else ""
        if has_media:
            media_number = len(json_response["includes"]["media"])
            links = text.rsplit('https://', media_number)
            text = links[0] if len(links) > 1 else ""
        
        if text == "":
            return None
        
        translation = emojis[tag] + ": "
        translation += self.trans.translate(text, src='th', dst='en').text
        return translation

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response,
                            indent=4, sort_keys=True))
                
                tweet_id = json_response["data"]["id"]
                self.like(tweet_id)

                tag = json_response["matching_rules"][0]["tag"]

                translation = self.translate_tweet(json_response["data"], json_response, tag)
                length = 280 - len(translation)
                if "referenced_tweets" in json_response["data"]:
                    parent = self.get_tweet(json_response["data"]["referenced_tweets"][0]["id"]).json()
                    print(parent)
                    username = parent["includes"]["users"][0]["username"]
                    if username not in [twitter_handles["becky"], twitter_handles["freen"]]:
                        if username in twitter_handles.values():
                            tag = list(twitter_handles.keys())[list(twitter_handles.values()).index(username)]
                        else:
                            tag = "other"
                        temp = self.translate_tweet(parent["data"][0], parent, tag)
                        translation = (temp + "\n" + translation) if (len(temp) < 280) else (temp[:(length-5)] + "...\n" + translation)

                if translation != None:
                    self.create_tweet(text=translation, in_reply_to_tweet_id=tweet_id)
                    self.create_tweet(text=translation, quote_tweet_id=tweet_id)
                else:
                    self.retweet(tweet_id)

    def interact(self):
        response = self.get_stream()
        self.last_response_time = time.time()
        t_handler = threading.Thread(target=self.response_handler(response))
        t_handler.start()
        while True:
            if (time.time() - self.last_response_time) > 30:
                logger.info("About to disconnect.")
                t_handler.join()
                logger.info("Disconnected.")
                t_handler = threading.Thread(target=self.response_handler(response))
                t_handler.start()
            time.sleep(10)

def main():
    ti = Twitter_Interacter()
    t_interact = threading.Thread(target=ti.interact)
    t_interact.start()

if __name__ == "__main__":
    main()
