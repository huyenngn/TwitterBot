import os
from src.bot import TranslateTweetsBot
from src.modules.twitter import Client, StreamClient

bot_settings = {
    # test users and admins
    "admins": ["FreenBeckyBot", "joohwangblink"],
    # twitter users and their respective emoji/alias
    # this could be accounts your biases regularily interact with
    # (including your biases)
    "twitter_handles": {
        "srchafreen": "\ud83d\udc30",
        "AngelssBecky": "\ud83e\udda6"
    },
}


translation_settings = {
    # language settings
    "src": "th",
    "dst": "en",
    # replacements applied before translating
    "glossary": {
        "มามี้": "Mami",
        "ปีโย๊": "Piyo",
        "ฟรีนกี้": "Freenky",
        "พี่ฟรีน": "P'Freen",
        "ฟรีน": "Freen",
        "คุณสาม": "คุณแซม",  # Khun Sam
        "น้องพุง": "Nong Belly",
        "น้อง": "Nong",
        "คุณ": "Khun",
    },
    # replacements applied after translating
    "corrections": {
        "Beck ": "Bec ",
        "I am": "",
        "I'm ": "",
        "I ": "",
        " me ": " me/you ",
        " me.": " me/you.",
        "boyfriend": "girlfriend",
        " him ": " her ",
        " him.": " her.",
        "his ": "her ",
    },
}

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

def main():
    api = Client(consumer_key,consumer_secret,access_token, access_token_secret)
    streamapi = StreamClient(bearer_token)
    bot = TranslateTweetsBot(
        src=translation_settings["src"],
        dst=translation_settings["dst"],
        glossary=translation_settings["glossary"],
        corrections=translation_settings["corrections"],
        admins=bot_settings["admins"],
        handles=bot_settings["twitter_handles"],
        api=api,
        streamapi=streamapi
        )
    bot.start()


if __name__ == "__main__":
    main()
