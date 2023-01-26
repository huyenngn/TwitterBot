import threading
import json
import time
from translate import Translator
from config import API
from helpers import logger

twitter_handles = {
    "freen": "srchafreen",
    "becky": "AngelssBecky",
    "nam": "namorntaraaa",
    "gap": "GAPtheseries",
    "bot": "FreenBeckyBot"
}

emojis = {
    "freen":  "\ud83d\udc30",
    "becky": "\ud83e\udda6",
    "nam": "\ud83d\udea2",
    "gap": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
    "other": "\ud83d\udc64",
    "bot": "\ud83e\udd16"
}

stream_rules = [
    # {"value": 'from:joohwangblink -is:retweet', "tag": "freenbeck"},
    {"value": '@FreenBeckyBot -from:FreenBeckyBot -to:FreenBeckyBot is:reply -is:retweet', "tag": "mention"},
    # {"value": 'retweets_of:FreenBeckyBot OR to:FreenBeckyBot', "tag": "interact"},
    {"value": '(from:'+twitter_handles["freen"]+' OR from:'+twitter_handles["becky"]+') -is:retweet', "tag": "freenbeck"},
]

class Twitter_Interacter(API):
    def __init__(self):
        self.trans = Translator()
        self.last_response_time = None

        super(Twitter_Interacter, self).__init__()

    def translate_tweet(self, json_response, tweet_id):
        is_quote = ("referenced_tweets" in json_response["data"]) and (
            json_response["data"]["referenced_tweets"][0]["type"] == "quoted")
        is_reply = ("referenced_tweets" in json_response["data"]) and (
            json_response["data"]["referenced_tweets"][0]["type"] == "replied_to")
        has_media = "media" in json_response["includes"]

        text = json_response["data"]["text"]

        if is_quote:
            text = text.rsplit(' ', 1)[0]
        if is_reply:
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split('@', reply_number)[-1].split(' ', 1)
            text = mentions[-1] if len(mentions) > 1 else ""
        if has_media and text != "":
            media_number = len(json_response["includes"]["media"])
            links = text.rsplit('https://', media_number)
            text = links[0] if len(links) > 1 else text

        username = json_response["includes"]["users"][0]["username"]
        if username in twitter_handles.values():
            emoji = list(twitter_handles.keys())[list(twitter_handles.values()).index(username)]
        else:
            emoji = "other"
        
        translation = emojis[emoji] + ": "
        translation += self.trans.translate_text(text).replace("#", "#.")

        reply_id = tweet_id
        is_thread = False
        while 250 < len(translation):
            parts = translation[247:].split(" ", 1)
            temp = translation[:247]+ parts[0] + "..."
            new_tweet = self.create_tweet(text=temp, in_reply_to_tweet_id=reply_id)
            if not is_thread:
                result = new_tweet
                is_thread = True
            reply_id = new_tweet["data"]["id"]
            translation = "..." + parts[-1]

        new_tweet = self.create_tweet(text=translation, in_reply_to_tweet_id=reply_id)
        if not is_thread:
            result = new_tweet

        return result

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response,
                            indent=4, sort_keys=True))

                tag = json_response["matching_rules"][0]["tag"]

                if tag == "mention":
                    print("meow1")
                    # get parent and translate parent reply to child#
                    tweet_id = json_response["data"]["id"]
                    parent_id = json_response["data"]["referenced_tweets"][0]["id"]
                    parent = self.get_tweet(parent_id)
                    logger.info(json.dumps(parent,
                            indent=4, sort_keys=True))
                    mentioned = False
                    for user in parent["includes"]["users"]:
                        if self.id == user["id"]:
                            mentioned = True
                    if not mentioned:
                        new_tweet = self.translate_tweet(parent, tweet_id)
                # elif tag == "interact":
                #     tweet_id = json_response["data"]["id"]
                #     self.like(tweet_id)
                elif tag == "freenbeck":
                    print("meow")
                    # translate tweet reply to tweet
                    # if has parent translate parent reply to tweets translation
                    tweet_id = json_response["data"]["id"]
                    self.like(tweet_id)
                    self.retweet(tweet_id)
                    new_tweet = self.translate_tweet(json_response, tweet_id)
                    tweet_id = new_tweet["data"]["id"]
                    self.retweet(tweet_id)
                    if "referenced_tweets" in json_response["data"]:
                        print("meow4")
                        parent_id = json_response["data"]["referenced_tweets"][0]["id"]
                        parent = self.get_tweet(parent_id)
                        username = parent["includes"]["users"][0]["username"]
                        if username not in [twitter_handles["becky"], twitter_handles["freen"]]:
                            new_tweet = self.translate_tweet(parent, tweet_id)
                            print("meow5")
                else:
                    pass
                # for m in json_response["includes"]["media"]:
                    # translation = translation + "\n image: " + self.trans.translate_image(url=m["url"])
                    # id = self.post_media(img)
                    # medias.append(id)

    def start(self):
        response = self.get_stream(stream_rules)
        self.last_response_time = time.time()
        t_handler = threading.Thread(target=self.response_handler(response))
        t_handler.start()
        while True:
            time.sleep(10)
            if (time.time() - self.last_response_time) > 30:
                logger.info("About to disconnect.")
                t_handler.join()
                logger.info("Disconnected.")
                t_handler = threading.Thread(target=self.response_handler(response))
                t_handler.start()
