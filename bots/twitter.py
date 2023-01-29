import json
import threading
import time
from api import TwitterAPI
from translate import ContentTranslator
from setup import logger, settings

class Twitter_Interacter(TwitterAPI):
    def __init__(self, api=None):
        self.trans = ContentTranslator()
        self.last_response_time = None
        super(Twitter_Interacter, self).__init__(api)

    def create_rules(self):
        rule = "("
        for bias in settings["biases"]:
            rule += "from:"+settings["twitter_handles"][bias]+" OR "
        rule = rule[:-4]+")"

        admin_rule = "t35t is:reply -to:"+self.username+" ("
        for admin in settings["admins"]:
            admin_rule += "from:"+admin+" OR "
        admin_rule = admin_rule[:-3]+"from:"+self.username+") -is:retweet"

        rules = [
            {"value": admin_rule, "tag": "admin"},
            {"value": "@"+self.username+" is:reply -from:"+self.username+" -to:"+self.username+" -is:retweet", "tag": "mention"},
            {"value": rule, "tag": "update"},
        ]
        return rules
    
    def get_data(self, json_response):
        is_quote = ("referenced_tweets" in json_response["data"]) and (
            json_response["data"]["referenced_tweets"][0]["type"] == "quoted")
        is_reply = ("referenced_tweets" in json_response["data"]) and (
            json_response["data"]["referenced_tweets"][0]["type"] == "replied_to")
        has_media = "media" in json_response["includes"]

        text = json_response["data"]["text"]
        image_urls = []

        if is_quote:
            text = text.rsplit(' ', 1)[0]
        if is_reply:
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split('@', reply_number)[-1].split(' ', 1)
            text = mentions[-1] if len(mentions) > 1 else ""
        if has_media and text != "":
            medias = json_response["includes"]["media"]
            for media in medias:
                if media["type"] == "photo":
                    image_urls.append(media["url"])
            links = text.rsplit('https://', len(medias))
            text = links[0] if len(links) > 1 else text

        username = json_response["includes"]["users"][0]["username"]
        tweet_id = json_response["data"]["id"]

        if "referenced_tweets" in json_response["data"]:
            parent_id = json_response["data"]["referenced_tweets"][0]["id"]
        else:
            parent_id = None

        return (text, username, tweet_id, parent_id, image_urls)
    
    def send_tweet(self, username, text, tweet_id, medias):
        if username in settings["twitter_handles"].values():
            emoji = list(settings["twitter_handles"].keys())[list(settings["twitter_handles"].values()).index(username)]
            translation = settings["emojis"][emoji] + ": "
            translation += text.replace("#", "#.")
        else:
            translation = "["+text.replace("#", "#.")+"]"

        reply_id = tweet_id
        if 250 < len(translation):
            last_part = translation[247:].split(" ", 1)
            first_part = translation[:247]+ last_part[0] + "..."
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

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response,
                            indent=4, sort_keys=True))
                
                tag = json_response["matching_rules"][0]["tag"]

                if tag == "mention":
                    x, y, tweet_id, parent_id, z = self.get_data(json_response)
                    parent = self.get_tweet(parent_id)
                    logger.info(json.dumps(parent,
                            indent=4, sort_keys=True))
                    text, username, x, a, z = self.get_data(parent)
                    mentioned = False
                    if ("entities" in parent["data"]) and ("mentions" in parent["data"]["entities"]):
                        for user in parent["data"]["entities"]["mentions"]:
                            if self.username == user["username"]:
                                mentioned = True
                                break
                    if not mentioned:
                        translation = self.trans.google_translate(text)
                        self.send_tweet(username, translation, tweet_id, [])

                elif tag == "update":
                    text, username, tweet_id, parent_id, image_urls = self.get_data(json_response)
                    self.like(tweet_id)
                    self.retweet(tweet_id)
                    translation = self.trans.translate_text(text)
                    translated_images = []
                    if image_urls:
                        for url in image_urls:
                            raw_image = self.trans.translate_image(url)
                            media_id = self.create_media(raw_image)["media_id"]
                            translated_images.append(str(media_id))
                    new_tweet = self.send_tweet(username, translation, tweet_id, translated_images)
                    tweet_id = new_tweet["data"]["id"]
                    self.retweet(tweet_id)
                    if parent_id != None:
                        parent = self.get_tweet(parent_id)
                        text, username, x, y, z = self.get_data(parent)
                        name = list(settings["twitter_handles"].keys())[list(settings["twitter_handles"].values()).index(username)]
                        if name not in settings["biases"]:
                            translation = self.trans.translate_text(text)
                            self.send_tweet(username, translation, tweet_id, [])

                elif tag == "admin":
                    x, y, tweet_id, parent_id, z = self.get_data(json_response)
                    parent = self.get_tweet(parent_id)
                    text, username, x, a, image_urls = self.get_data(parent)
                    translation = self.trans.translate_text(text)
                    translated_images = []
                    if image_urls:
                        for url in image_urls:
                            raw_image = self.trans.translate_image(url)
                            media_id = self.create_media(raw_image)["media_id"]
                            translated_images.append(str(media_id))
                    self.send_tweet(username, translation, tweet_id, translated_images)

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


