import json
import logging
import threading
from src.modules.thai2eng import Thai2Eng
from src.modules.twitter import Client, StreamClient
from src.modules.translate import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslateTweetsBot():
    def __init__(self, src, dst, glossary={}, corrections={}, admins=[], handles={}, api=None, streamapi=None):
        self.tl = Translator(src=src, dst=dst, glossary=glossary, corrections=corrections)
        self.t2e = Thai2Eng()
        self.biases = handles.keys()
        self.admins = admins
        self.handles = handles
        self.api = api
        self.streamapi = streamapi

    def create_rules(self):
        rule = "("
        for bias in self.biases:
            rule += "from:" + bias + " OR "
        rule = rule[:-4] + ")"

        rules = [
            {"value": "\"@" + self.api.username + " tl\" is:reply -to:" + self.api.username + " -from:" + self.api.username + " -is:retweet", "tag": "mention"},
            {"value": rule, "tag": "update"},
            {"value": "t35t from:FreenBeckybot -is:retweet -is:reply", "tag": "update"}
        ]
        return rules

    def get_data(self, json_response):
        if "referenced_tweets" in json_response["data"]:
            tweet_type = json_response["data"]["referenced_tweets"][0]["type"]
            parent_id = json_response["data"]["referenced_tweets"][0]["id"]
        else:
            tweet_type = ""
            parent_id = ""

        text = " " + json_response["data"]["text"].encode('utf-16', 'surrogatepass').decode('utf-16', 'surrogatepass') + " "
        if tweet_type == "quoted":
            parts = text.rsplit("https://", 1)
            tail = parts[-1].split(" ", 1)
            text = parts[0] + (tail[-1] if len(tail) > 1 else "")

        image_urls = []
        text = " " + text + " "
        if "media" in json_response["includes"]:
            is_photo = False
            medias = json_response["includes"]["media"]
            for media in medias:
                if media["type"] == "photo":
                    image_urls.append(media["url"])
                    is_photo = True
            
            if is_photo:
                parts = text.rsplit("https://", 1)
                tail = parts[-1].split(" ", 1)
                text = parts[0] + (tail[-1] if len(tail) > 1 else "")

        text = " " + text + " "
        if tweet_type == "replied_to":
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split("@", reply_number)
            text = ""
            for mention in mentions:
                temp = mention.split(" ", 1)
                text += temp[-1] if len(temp) > 1 else ""

        username = json_response["includes"]["users"][0]["username"]
        tweet_id = json_response["data"]["id"]
        reply_settings = json_response["data"]["reply_settings"]

        return (" ".join(text.split()), username, tweet_id, parent_id, image_urls, tweet_type, reply_settings)

    def send_tweet(self, username, text, tweet_id, medias, reference, reply_settings):
        translation = ""
        if username in self.handles.keys():
            translation += self.handles[username] + ": "
        translation += text
        if reference is not None:
            translation = ("[" + self.handles[reference[1]] + " " + reference[0] + "] " + translation)

        translation = translation.replace("#", "#.")

        last_part = translation[250:].split(" ", 1)
        if len(last_part) > 1:
            first_part = translation[:250] + last_part[0] + "..."
            params = {"text": first_part}
            if reply_settings == "everyone":
                params["reply.in_reply_to_tweet_id"] = tweet_id
            else:
                params["quote_tweet_id"] = tweet_id

            if medias:
                params["media.media_ids"] = medias

            new_tweet = self.api.create_tweet(params)
            translation = "..." + last_part[-1]
            params = {"text": translation,
                      "reply.in_reply_to_tweet_id": new_tweet["data"]["id"]}
            self.api.create_tweet(params)
        else:
            params = {"text": translation}
            if reply_settings == "everyone":
                params["reply.in_reply_to_tweet_id"] = tweet_id
            else:
                params["quote_tweet_id"] = tweet_id

            if medias:
                params["media.media_ids"] = medias

            new_tweet = self.api.create_tweet(params)

        return new_tweet

    def explanation_tweet(self, text, tweet_id):
        definitions = self.t2e.get_definition(text)
        translated_images = []
        for definition in definitions:
            media_id = self.api.create_image(definition)["media_id"]
            translated_images.append(str(media_id))
        new_tweet = self.send_tweet(
            "", "explanation:", tweet_id, translated_images, None, "everyone"
        )
        return new_tweet["data"]["id"]

    def translation_tweet(self, text, username, tweet_id, image_urls, *, reference=None, reply_settings="everyone"):
        translation = self.tl.translate_text(text)
        translated_images = []
        if image_urls:
            for url in image_urls:
                raw_image = self.tl.translate_image(url)
                media_id = self.api.create_image(raw_image)["media_id"]
                translated_images.append(str(media_id))

        new_tweet = self.send_tweet(
            username, translation, tweet_id, translated_images, reference, reply_settings
        )
        return new_tweet["data"]["id"]

    def start(self):
        for json_response in self.streamapi.get_filter():
            tag = json_response["matching_rules"][0]["tag"]
            if tag == "update":
                text, username, tweet_id, parent_id, image_urls, tweet_type, reply_settings = self.get_data(json_response)
                self.api.like(tweet_id)
                self.api.retweet(tweet_id)
                if tweet_type != "retweeted":
                    tweet_id = self.translation_tweet(text, username, tweet_id, image_urls, reply_settings=reply_settings)
                    self.api.retweet(tweet_id)
                    self.explanation_tweet(text, tweet_id)
                if parent_id:
                    parent = self.api.get_tweet(parent_id)
                    text, parentname, _, _, image_urls, _, _ = self.get_data(parent)
                    if parentname not in self.biases:
                        tweet_id = self.translation_tweet(text, parentname, tweet_id, image_urls, reference=(tweet_type, username))
                        if tweet_type == "retweeted":
                            self.api.retweet(tweet_id)
                            self.explanation_tweet(text, tweet_id)

            elif tag == "mention":
                _, _, tweet_id, parent_id, _, _, reply_settings = self.get_data(json_response)
                parent = self.api.get_tweet(parent_id)
                logger.info(json.dumps(parent, indent=4, sort_keys=True))

                text, username, _, _, image_urls, _, _ = self.get_data(parent)

                tweet_id = self.translation_tweet(text, username, tweet_id, image_urls, reply_settings=reply_settings)
                self.explanation_tweet(text, tweet_id)