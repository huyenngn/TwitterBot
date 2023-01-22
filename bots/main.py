from googletrans import Translator
import threading
from config import *


class Twitter_Interacter(Twitter):
    def __init__(self):
        self.trans = Translator()
        self.last_response_time = None

        super(Twitter_Interacter, self).__init__()

    def translate_tweet(self, data, json_response, tag):
        is_quote = ("referenced_tweets" in data) and (
            data["referenced_tweets"][0]["type"] == "quoted")
        is_reply = ("referenced_tweets" in data) and (
            data["referenced_tweets"][0]["type"] == "replied_to")
        has_media = "media" in json_response["includes"]

        text = data["text"]

        if is_quote:
            text = text.rsplit(' ', 1)[0]
        if is_reply:
            reply_number = len(json_response["includes"]["users"]) - 1
            mentions = text.split('@', reply_number)[-1].split(' ', 1)
            text = mentions[-1] if len(mentions) > 1 else ""
        if has_media:
            media_number = len(json_response["includes"]["media"])
            links = text.rsplit('https://', media_number)
            text = links[0] if len(links) > 1 else ""
        
        if text == "":
            return None
        
        translation = emojis[tag] + ": "
        translation += self.trans.translate(text, src='th', dst='en').text
        return translation

    def response_handler(self, response):
        for response_line in response.iter_lines():
            self.last_response_time = time.time()
            if response_line:
                json_response = json.loads(response_line)
                logger.info(json.dumps(json_response,
                            indent=4, sort_keys=True))
                
                tweet_id = json_response["data"]["id"]
                self.like(tweet_id)

                tag = json_response["matching_rules"][0]["tag"]

                translation = self.translate_tweet(json_response["data"], json_response, tag)
                length = 280 - len(translation)
                if "referenced_tweets" in json_response["data"]:
                    parent = self.get_tweet(json_response["data"]["referenced_tweets"][0]["id"]).json()
                    print(parent)
                    username = parent["includes"]["users"][0]["username"]
                    if username not in [twitter_handles["becky"], twitter_handles["freen"]]:
                        if username in twitter_handles.values():
                            tag = list(twitter_handles.keys())[list(twitter_handles.values()).index(username)]
                        else:
                            tag = "other"
                        temp = self.translate_tweet(parent["data"][0], parent, tag)
                        translation = (temp + "\n" + translation) if (len(temp) < 280) else (temp[:(length-5)] + "...\n" + translation)

                if translation != None:
                    self.create_tweet(text=translation, in_reply_to_tweet_id=tweet_id)
                    self.create_tweet(text=translation, quote_tweet_id=tweet_id)
                else:
                    self.retweet(tweet_id)

    def interact(self):
        response = self.get_stream()
        self.last_response_time = time.time()
        t_handler = threading.Thread(target=self.response_handler(response))
        t_handler.start()
        while True:
            if (time.time() - self.last_response_time) > 30:
                logger.info("About to disconnect.")
                t_handler.join()
                logger.info("Disconnected.")
                t_handler = threading.Thread(target=self.response_handler(response))
                t_handler.start()
            time.sleep(10)

def main():
    ti = Twitter_Interacter()
    t_interact = threading.Thread(target=ti.interact)
    t_interact.start()

if __name__ == "__main__":
    main()
