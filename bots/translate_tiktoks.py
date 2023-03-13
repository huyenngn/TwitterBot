import logging
import time
from TikTokApi import TikTokApi
from bots.modules.twitter import Twitter
from bots.modules.translate import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslateTikToksBot(Twitter):
    def __init__(self, src, dst, glossary={}, corrections={}, handles={}, emojis={}, api=None):
        self.tl = Translator(src=src, dst=dst, glossary=glossary, corrections=corrections)
        self.tiktok = TikTokApi()
        self.last_response_time = None
        self.users = []
        for user in handles.keys():
            self.users.append(self.tiktok.user(username=user))
        self.handles = handles
        self.emojis = emojis
        self.ids = []
        for user in self.users:
            video = user.videos(count=1)
            self.ids.append(video.id)
        super().__init__(api)

    def send_tweet(self, username, text, medias):
        translation = (self.emojis[self.handles[username]] + " tiktiok update" + text)
        translation = translation.replace("#", "#.")

        last_part = translation[250:].split(" ", 1)
        if len(last_part) > 1:
            first_part = translation[:250] + last_part[0] + "..."
            new_tweet = self.create_tweet(text=first_part, media_ids=medias)
            translation = "..." + last_part[-1]
            self.create_tweet(text=translation, in_reply_to_tweet_id=new_tweet["data"]["id"])
        else:
            self.create_tweet(text=translation, media_ids=medias)

    def translate_tiktok(self, username, video):
        media_id = self.create_video(video.bytes())
        self.send_tweet(username, "", [media_id])

    def start(self):
        while True:
            for user in self.users:
                video = user.videos(count=1)
                if video.id not in self.ids:
                    self.ids.append(video.id)
                    self.translate_tiktok(user.username, video)
            time.sleep(600)
