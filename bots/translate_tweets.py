import json
import logging
import threading
import time
from bots.modules.thai2eng import get_definition
from bots.modules.twitter import Twitter
from bots.modules.translate import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslateTweetsBot(Twitter):
    def __init__(self, biases, src, dst, glossary={}, corrections={}, admins=[], handles={}, api=None):
        self.tl = Translator(src=src, dst=dst, glossary=glossary, corrections=corrections)
        self.last_response_time = None
        self.biases = biases
        self.admins = admins
        self.handles = handles
        super().__init__(api)

    def create_rules(self):
        rule = "("
        for bias in self.biases:
            rule += "from:" + bias + " OR "
        rule = rule[:-4] + ")"

        rules = [
            {"value": "\"@" + self.username + " tl\" is:reply -to:" + self.username + " -is:retweet", "tag": "mention"},
            {"value": rule, "tag": "update"},
        ]
        return rules

    def get_data(self, json_response):
        if "referenced_tweets" in json_response["data"]:
            tweet_type = json_response["data"]["referenced_tweets"][0]["type"]
            parent_id = json_response["data"]["referenced_tweets"][0]["id"]
        else:
            tweet_type = ""
            parent_id = ""

        text = " " + json_response["data"]["text"] + " "
        if tweet_type == "quoted":
            parts = text.rsplit("https://", 1)
            tail = parts[-1].split(" ", 1)
            text = parts[0] + (tail[-1] if len(tail) > 1 else "")

        if tweet_type == "replied_to":
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split("@", reply_number)

            text = ""
            for mention in mentions:
                temp = mention.split(" ", 1)
                text += temp[-1] if len(temp) > 1 else ""

        image_urls = []
        if "media" in json_response["includes"]:
            medias = json_response["includes"]["media"]
            for media in medias:
                if media["type"] == "photo":
                    image_urls.append(media["url"])

            links = text.rsplit("https://", len(medias))
            text = ""
            for link in links:
                temp = link.split(" ", 1)
                text += temp[-1] if len(temp) > 1 else ""

        username = json_response["includes"]["users"][0]["username"]
        tweet_id = json_response["data"]["id"]

        return (" ".join(text.split()), username, tweet_id, parent_id, image_urls, tweet_type)

    def send_tweet(self, username, text, tweet_id, medias, *, reference=None):
        translation = ""
        if username in self.handles.keys():
            translation += self.handles[username] + ": "
        translation += text
        if reference is not None:
            translation = ("[" + self.handles[reference[1]] + " " + reference[0] + "] " + translation)

        translation = translation.replace("#", "#.")

        reply_id = tweet_id
        if 250 < len(translation):
            last_part = translation[247:].split(" ", 1)
            first_part = translation[:247] + last_part[0] + "..."
            if medias:
                new_tweet = self.create_tweet(text=first_part, in_reply_to_tweet_id=reply_id, media_ids=medias)
            else:
                new_tweet = self.create_tweet(text=first_part, in_reply_to_tweet_id=reply_id)
            reply_id = new_tweet["data"]["id"]
            translation = "..." + last_part[-1]
            self.create_tweet(text=translation, in_reply_to_tweet_id=reply_id)
        else:
            if medias:
                new_tweet = self.create_tweet(text=translation, in_reply_to_tweet_id=reply_id, media_ids=medias)
            else:
                new_tweet = self.create_tweet(text=translation, in_reply_to_tweet_id=reply_id)

        return new_tweet

    def explanation_tweet(self, text, tweet_id):
        definitions = get_definition(text)
        translated_images = []
        for definition in definitions:
            media_id = self.create_media(definition)["media_id"]
            translated_images.append(str(media_id))
        new_tweet = self.send_tweet(
            "", "explanation:", tweet_id, translated_images
        )
        return new_tweet["data"]["id"]

    def translation_tweet(self, text, username, tweet_id, image_urls, reference):
        translation = self.tl.translate_text(text)
        translated_images = []
        if image_urls:
            for url in image_urls:
                raw_image = self.tl.translate_image(url)
                media_id = self.create_media(raw_image)["media_id"]
                translated_images.append(str(media_id))

        new_tweet = self.send_tweet(
            username, translation, tweet_id, translated_images, reference=reference
        )
        return new_tweet["data"]["id"]

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response, indent=4, sort_keys=True))

                tag = json_response["matching_rules"][0]["tag"]

                if tag == "update":
                    (text, username, tweet_id, parent_id, image_urls, tweet_type) = self.get_data(json_response)
                    self.like(tweet_id)
                    self.retweet(tweet_id)
                    tweet_id = self.translation_tweet(text, username, tweet_id, image_urls, None)
                    self.retweet(tweet_id)
                    if len(text) > 15:
                        tweet_id = self.explanation_tweet(text, tweet_id)
                    if parent_id and tweet_type != "retweeted":
                        parent = self.get_tweet(parent_id)
                        text, parentname, x, y, image_urls, z = self.get_data(parent)
                        if parentname not in self.biases:
                            tweet_id = self.translation_tweet(text, parentname, tweet_id, image_urls, (tweet_type, username))

                elif tag == "mention":
                    x, y, tweet_id, parent_id, z, a = self.get_data(json_response)
                    parent = self.get_tweet(parent_id)
                    logger.info(json.dumps(parent, indent=4, sort_keys=True))

                    text, username, x, y, image_urls, z = self.get_data(parent)

                    tweet_id = self.translation_tweet(text, username, tweet_id, image_urls, None)
                    if len(text) > 15:
                        self.explanation_tweet(text, tweet_id)

    def start(self):
        response = self.get_stream()
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