import os
import time
import requests
from translate import Translator
from api import TwitterAPI
from setup import logger, settings

access_token = os.getenv("GCLOUD_PROJECT")
handles = settings["insta_handles"]

class Instagram_Reposter(TwitterAPI):
    def __init__(self, api):
        self.trans = Translator()
        super().__init__(api=api)

    def get_recents(self, user_id):
        response = requests.get(
            "https://graph.instagram.com/v15.0/tweets/{}/media".format(user_id),
            params={
                "access_token": self.access_token,
                "fields": "id,caption,media_url,timestamp,username",
                "since": self.last_checked_time}
        )
        logger.info(f"Got recent Instagram posts. Response code: {response.status_code}")

        if response.status_code != 200:
            # TODO: error handler
            return self.get_recents(user_id)

        return response.json()
    
    def start(self):
        while True:
            for handle in handles.values():
                response = self.get_recents(handle)
                for post in response["data"]:
                    text = post["caption"]
                    translation = post["timestamp"][2:].replace("-", "") + " " + post["username"] + " new ig post:\n"
                    translation += "\"" + self.trans.translate_text(text) + "\"\n" + post["media_url"]
                    self.create_tweet(text=translation)
                time.sleep(600)
