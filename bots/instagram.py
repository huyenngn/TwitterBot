import time
import requests
from config import API, error_handler
from translate import Translator
from helpers import logger

insta_ids = ["eafsdfas", "aefsfSFD"]

class Instagram_Reposter(API):
    def __init__(self):
        self.trans = Translator()
        self.last_checked_time = time.time()
        self.access_token = "weqweq"
        super().__init__()

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
            error_handler(response, self.wait_time)
            return self.get_recents(user_id)

        return response.json()
    
    def start(self):
        toggle = True
        while True:
            response = self.get_recents(insta_ids[int(toggle)])
            for post in response["data"]:
                text = post["caption"]
                translation = post["timestamp"][2:].replace("-", "") + " " + post["username"] + " new ig post:\n"
                translation += "\"" + self.trans.translate_text(text) + "\"\n" + post["media_url"]
                self.create_tweet(text=translation)
            
            toggle = not toggle
            time.sleep(600)
