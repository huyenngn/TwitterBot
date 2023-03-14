import logging
import time
from urllib.request import urlopen
from tiktokapipy.api import TikTokAPI
from bots.modules.twitter import Twitter
from bots.modules.translate import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslateTikToksBot(Twitter):
    def __init__(
        self, src, dst, glossary={}, corrections={}, handles={}, emojis={}, api=None
    ):
        self.tl = Translator(
            src=src, dst=dst, glossary=glossary, corrections=corrections
        )
        self.tiktok = TikTokAPI()
        self.last_response_time = None
        self.emojis = emojis
        self.handles = handles
        self.ids = []
        for handle in self.handles:
            for video in self.tiktok.user(handle).videos:
                self.ids.append(video.id)
        super().__init__(api)

    def send_tweet(self, username, text, medias):
        translation = (
            self.emojis[self.handles[username]] + " tiktiok update:\n\n" + text
        )
        translation = translation.replace("#", "#.")

        last_part = translation[250:].split(" ", 1)
        if len(last_part) > 1:
            first_part = translation[:250] + last_part[0] + "..."
            new_tweet = self.create_tweet(text=first_part, media_ids=medias)
            translation = "..." + last_part[-1]
            self.create_tweet(
                text=translation, in_reply_to_tweet_id=new_tweet["data"]["id"]
            )
        else:
            self.create_tweet(text=translation, media_ids=medias)

    def translate_tiktok(self, username, video):
        link = video.video.download_addr
        raw_bytes = urlopen(link).read()

        media_id = self.create_video(raw_bytes)
        text = video.desc
        text = self.tl.translate_text(text)
        self.send_tweet(username, text, [media_id])

    def start(self):
        while True:
            for handle in self.handles:
                user = self.tiktok.user(handle)
                for video in user.videos:
                    if video.id not in self.ids:
                        self.ids.append(video.id)
                        self.translate_tiktok(user.nickname, video)
            time.sleep(600)
