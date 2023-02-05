import json
import threading
import time
from api import TwitterAPI
from translate import ContentTranslator
from setup import logger, bot_settings
from thai2eng import get_definition


class Twitter_Interacter(TwitterAPI):
    def __init__(self, api=None):
        self.trans = ContentTranslator()
        self.last_response_time = None
        super(Twitter_Interacter, self).__init__(api)

    def create_rules(self):
        rule = "("
        for bias in bot_settings["biases"]:
            rule += "from:" + bias + " OR "
        rule = rule[:-4] + ")"

        rules = [
            {
                "value": "@"
                + self.username
                + " is:reply -to:"
                + self.username
                + " -is:retweet",
                "tag": "mention",
            },
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

    def send_tweet(self, username, text, tweet_id, medias, *, reference=("", "")):
        translation = ""
        if reference:
            translation += bot_settings["twitter_handles"][reference[1]] + " " + reference[0] + " "
        if username in bot_settings["twitter_handles"].keys():
            translation += bot_settings["twitter_handles"][username] + ": "
        translation += text

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
                        translation = self.trans.translate_text(text)
                        translated_images = []
                        if image_urls:
                            for url in image_urls:
                                raw_image = self.trans.translate_image(url)
                                media_id = self.create_media(raw_image)["media_id"]
                                translated_images.append(str(media_id))
                        else:
                            raw_image = get_definition(text)
                            if raw_image.status_code == 200:
                                media_id = self.create_media(raw_image.content)["media_id"]
                                translated_images.append(str(media_id))

                        new_tweet = self.send_tweet(
                            username, translation, tweet_id, translated_images, ""
                        )
                        tweet_id = new_tweet["data"]["id"]
                        self.retweet(tweet_id)
                    if parent_id:
                        parent = self.get_tweet(parent_id)
                        text, parentname, x, y, z, a = self.get_data(parent)
                        if parentname not in bot_settings["biases"]:
                            translation = self.trans.translate_text(text)
                            translated_images = []
                            if image_urls:
                                for url in image_urls:
                                    raw_image = self.trans.translate_image(url)
                                    media_id = self.create_media(raw_image)["media_id"]
                                    translated_images.append(str(media_id))
                            new_tweet = self.send_tweet(
                                parentname,
                                translation,
                                tweet_id,
                                translated_images,
                                (tweet_type, username)
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
                        translation = self.trans.translate_text(text)
                        translated_images = []
                        if username in bot_settings["admins"]:
                            for url in image_urls:
                                raw_image = self.trans.translate_image(url)
                                media_id = self.create_media(raw_image)["media_id"]
                                translated_images.append(str(media_id))
                        self.send_tweet(
                            username, translation, tweet_id, translated_images, None
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


def main():
    text = " @gvedsbh https://gvedsbh 123456789 @gvedsbh https://gvedsbh 123456789 https://gvedsbh 123456789 https://gvedsbh "
    # raw_text = " 123456789 https://gvedsbh "
    # # raw_text = " https://gvedsbh 123456789 "
    # # raw_text = " https://gvedsbh "
    # # raw_text = " 123456789 https://gvedsbh 123456789 "

    parts = text.rsplit("https", 1)
    tail = parts[-1].split(" ", 1)
    text = parts[0] + (tail[-1] if len(tail) > 1 else "")

    # raw_text = " 123456789 @gvedsbh "
    # raw_text = " @gvedsbh 123456789 "
    # raw_text = " @gvedsbh "
    # raw_text = " 123456789 @gvedsbh 123456789 "
    # raw_text = " 123456789 @gvedsbh @gvedsbh "
    # raw_text = " @gvedsbh @gvedsbh 123456789 "
    # raw_text = " @gvedsbh 123456789 @gvedsbh "
    # raw_text = " 123456789 @gvedsbh 123456789 @gvedsbh "
    reply_number = 2
    mentions = text.split("@", reply_number)

    text = ""
    for mention in mentions:
        temp = mention.split(" ", 1)
        text += temp[-1] if len(temp) > 1 else ""

    links = text.rsplit("https://", 3)
    text = ""
    for link in links:
        temp = link.split(" ", 1)
        text += temp[-1] if len(temp) > 1 else ""

    text = " ".join(text.split())
    print(text, len(text))


if __name__ == "__main__":
    main()
