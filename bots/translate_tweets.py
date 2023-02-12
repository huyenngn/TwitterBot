import json
import logging
import threading
import time
from modules.thai2eng import get_definition
from modules.twitter import Twitter
from modules.translate import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_settings = {
    # twitter user the bot will automatically interact with
    "biases": ["srchafreen", "AngelssBecky"],
    # test users and admins
    "admins": ["FreenBeckyBot", "srchafreen", "AngelssBecky"],
    # twitter users and their respective emoji/alias
    # this could be accounts your biases regularily interact with
    # (including your biases)
    "twitter_handles": {
        "srchafreen": "\ud83d\udc30",
        "AngelssBecky": "\ud83e\udda6",
        "namorntaraaa": "\ud83d\udea2",
        "GAPtheseries": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
    },
}


class TranslateTweetsBot(Twitter):
    def __init__(self, api=None):
        self.tl = Translator()
        self.last_response_time = None
        super().__init__(api)

    def create_rules(self):
        rule = "("
        for bias in bot_settings["biases"]:
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

        return (
            " ".join(text.split()),
            username,
            tweet_id,
            parent_id,
            image_urls,
            tweet_type,
        )

    def send_tweet(self, username, text, tweet_id, medias, *, reference=None):
        translation = ""
        if username in bot_settings["twitter_handles"].keys():
            translation += bot_settings["twitter_handles"][username] + ": "
        translation += text
        if reference is not None:
            translation = (
                "["
                + bot_settings["twitter_handles"][reference[1]]
                + " "
                + reference[0]
                + "] "
                + translation
            )

        translation = translation.replace("#", "#.")

        reply_id = tweet_id
        if 250 < len(translation):
            last_part = translation[247:].split(" ", 1)
            first_part = translation[:247] + last_part[0] + "..."
            if medias:
                new_tweet = self.create_tweet(
                    text=first_part, in_reply_to_tweet_id=reply_id, media_ids=medias
                )
            else:
                new_tweet = self.create_tweet(
                    text=first_part, in_reply_to_tweet_id=reply_id
                )
            reply_id = new_tweet["data"]["id"]
            translation = "..." + last_part[-1]
            self.create_tweet(text=translation, in_reply_to_tweet_id=reply_id)
        else:
            if medias:
                new_tweet = self.create_tweet(
                    text=translation, in_reply_to_tweet_id=reply_id, media_ids=medias
                )
            else:
                new_tweet = self.create_tweet(
                    text=translation, in_reply_to_tweet_id=reply_id
                )

        return new_tweet

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response, indent=4, sort_keys=True))

                tag = json_response["matching_rules"][0]["tag"]

                if tag == "update":
                    (
                        text,
                        username,
                        tweet_id,
                        parent_id,
                        image_urls,
                        tweet_type,
                    ) = self.get_data(json_response)
                    self.like(tweet_id)
                    self.retweet(tweet_id)
                    if tweet_type != "retweeted":
                        translation = self.tl.translate_text(text)
                        translated_images = []
                        if image_urls:
                            for url in image_urls:
                                raw_image = self.tl.translate_image(url)
                                media_id = self.create_media(raw_image)["media_id"]
                                translated_images.append(str(media_id))

                        new_tweet = self.send_tweet(
                            username, translation, tweet_id, translated_images
                        )
                        tweet_id = new_tweet["data"]["id"]
                        self.retweet(tweet_id)
                        if len(text) > 15:
                            definitions = get_definition(text)
                            translated_images = []
                            for definition in definitions:
                                media_id = self.create_media(definition)["media_id"]
                                translated_images.append(str(media_id))
                            new_tweet = self.send_tweet(
                                "", "explanation:", tweet_id, translated_images
                            )
                            tweet_id = new_tweet["data"]["id"]
                    if parent_id:
                        parent = self.get_tweet(parent_id)
                        text, parentname, x, y, z, a = self.get_data(parent)
                        if parentname not in bot_settings["biases"]:
                            translation = self.tl.translate_text(text)
                            translated_images = []
                            if image_urls:
                                for url in image_urls:
                                    raw_image = self.tl.translate_image(url)
                                    media_id = self.create_media(raw_image)["media_id"]
                                    translated_images.append(str(media_id))
                            new_tweet = self.send_tweet(
                                parentname,
                                translation,
                                tweet_id,
                                translated_images,
                                reference=(tweet_type, username),
                            )
                            tweet_id = new_tweet["data"]["id"]
                            self.retweet(tweet_id)

                elif tag == "mention":
                    x, y, tweet_id, parent_id, z, a = self.get_data(json_response)
                    parent = self.get_tweet(parent_id)
                    logger.info(json.dumps(parent, indent=4, sort_keys=True))
                    text, username, x, y, image_urls, z = self.get_data(parent)
                    mentioned = False

                    if ("entities" in parent["data"]) and (
                        "mentions" in parent["data"]["entities"]
                    ):
                        for user in parent["data"]["entities"]["mentions"]:
                            if self.username == user["username"]:
                                mentioned = True
                                break
                    if not mentioned:
                        translation = self.tl.translate_text(text)
                        translated_images = []
                        if username in bot_settings["admins"]:
                            for url in image_urls:
                                raw_image = self.tl.translate_image(url)
                                media_id = self.create_media(raw_image)["media_id"]
                                translated_images.append(str(media_id))
                        new_tweet = self.send_tweet(
                            username, translation, tweet_id, translated_images
                        )
                        tweet_id = new_tweet["data"]["id"]
                        if len(text) > 15:
                            definitions = get_definition(text)
                            translated_images = []
                            for definition in definitions:
                                media_id = self.create_media(definition)["media_id"]
                                translated_images.append(str(media_id))
                            new_tweet = self.send_tweet(
                                "", "explanation:", tweet_id, translated_images
                            )

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
