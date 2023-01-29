import os
import time
import requests
from translate import ContentTranslator
from api import TwitterAPI
from setup import logger, settings

access_token = os.getenv("IG_ACCESS_TOKEN")

class Instagram_Reposter(TwitterAPI):
    def __init__(self, api=None):
        self.trans = ContentTranslator()
        t = time.time()
        self.last_checked_time = [t] * len(settings["biases"])
        super(Instagram_Reposter, self).__init__(api)

    def get_recents(self, user_id, index):
        response = requests.get(
            "https://graph.instagram.com/v15.0/tweets/{}/media".format(user_id),
            params={
                "access_token": access_token,
                "fields": "id,caption,media_url,timestamp,username",
                "since": self.last_checked_time[index]}
        )
        logger.info(f"Got recent Instagram posts. Response code: {response.status_code}")
        if response.status_code != 200:
            time.sleep(600)
            self.get_recents(user_id, index)

        return response.json()
    
    def start(self):
        while True:
            for index, key in enumerate(settings["biases"]):
                response = self.get_recents(settings["insta_ids"][key], index)
                self.last_checked_time[index] = time.time()
                logger.info(f"Fetching data for {key}")
                for post in response["data"]:
                    text = post["caption"]
                    translation = post["timestamp"][2:].replace("-", "") + " " + settings["emojis"][key] + post["username"] + " via Instagram:\n"
                    translation += "\"" + self.trans.translate_text(text) + "\"\n" + post["media_url"]
                    self.create_tweet(text=translation)
                time.sleep(600)
