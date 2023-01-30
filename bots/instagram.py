from io import BytesIO
import os
import time
import requests
from translate import ContentTranslator
from api import TwitterAPI
from setup import logger, settings
import collections
from instagrapi import Client

ig_username = os.getenv("IG_USERNAME")
ig_password = os.getenv("IG_PASSWORD")


class Instagram_Reposter(TwitterAPI):
    def __init__(self, api=None):
        self.trans = ContentTranslator()
        self.known_posts = collections.deque(maxlen=5)
        self.cl = Client()
        self.cl.login(ig_username, ig_password)
        super(Instagram_Reposter, self).__init__(api)

    def get_recents(self, username):
        user_id = self.cl.user_id_from_username(username)
        medias = self.cl.user_medias(user_id, 5)
        new_posts = []
        
        for media in medias:
            media_pk = media["pk"]
            if media_pk not in self.known_posts:
                self.known_posts.append(media_pk)
                text = media["caption_text"]
                url = "https://www.instagram.com/p/" + media["code"]
                t = media["taken_at"].strftime("%Y")[2:] + media["taken_at"].strftime("%m%d")
                response = requests.get(media["thumbnail_url"]).content
                buff = BytesIO(response)
                new_posts.append((text, url, t, buff.getvalue))
        
        return new_posts
    
    def start(self):
        while True:
            for key in settings["biases"]:
                username = settings["insta_handles"][key]
                new_posts = self.get_recents(username)
                logger.info(f"Fetching data for {key}")
                for post in new_posts:
                    text = post[2] + settings["emojis"][key] + username + " via IG:\n"
                    text += self.trans.translate_text(post[0]) + "(translated with GT)\n"
                    text += "> " + post[1]
                    media_id = self.create_media(post[3])["media_id"]
                    self.create_tweet(text=text, media_ids=[media_id])
                time.sleep(600)
