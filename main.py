import threading
from bots.translate_tweets import TranslateTweetsBot
from bots.translate_tiktoks import TranslateTikToksBot

bot_settings = {
    # twitter user the bot will automatically interact with
    "biases": ["srchafreen", "AngelssBecky"],
    # test users and admins
    "admins": ["FreenBeckyBot", "joohwangblink"],
    # twitter users and their respective emoji/alias
    # this could be accounts your biases regularily interact with
    # (including your biases)
    "twitter_handles": {
        "srchafreen": "freen",
        "AngelssBecky": "becky",
    },
    "tiktok_handles": {
        "srchafreen": "freen",
        "angelssbecky": "becky",
    },
    "emojis": {
        "freen": "\ud83d\udc30",
        "becky": "\ud83e\udda6",
    },
}

translation_settings = {
    # language settings
    "src": "th",
    "dst": "en",
    # replacements applied before translating
    "glossary": {
        # "ง้อ": "reconcile",
        # "งอน": "sulk",
        "มุมุ": "mumu",
        "มามี้": "Mami",
        "ยัก": "รัก",  # yak
        "ปีโย๊": "Piyo",
        "ฟรีนกี้": "Freenky",
        "พี่ฟรีน": "P'Freen",
        "ฟรีน": "Freen",
        "คุณสาม": "คุณแซม",  # Khun Sam
        "นุคน": "หนู",  # Nu -> Sandra
        "นุ": "หนู",
        "หนู": "แซนดร้า",
        "น้องพุง": "Nong Belly",
        "น้อง": "Nong",
        "พี่": "Phi",
        "คุณ": "Khun",
        # "อะ": "",  # a
    },
    # replacements applied after translating
    "corrections": {
        "Sandra": "Nu",
        "sandra": "Nu",
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


def main():
    ttw = TranslateTweetsBot(
        src=translation_settings["src"],
        dst=translation_settings["dst"],
        glossary=translation_settings["glossary"],
        corrections=translation_settings["corrections"],
        admins=bot_settings["admins"],
        handles=bot_settings["twitter_handles"],
        emojis=bot_settings["emojis"]
        )
    t_ttw = threading.Thread(target=ttw.start)
    t_ttw.start()
    api = ttw.get_api()
    ttt = TranslateTikToksBot(
        src=translation_settings["src"],
        dst=translation_settings["dst"],
        glossary=translation_settings["glossary"],
        corrections=translation_settings["corrections"],
        handles=bot_settings["tiktok_handles"],
        emojis=bot_settings["emojis"],
        api=api
        )
    t_ttt = threading.Thread(target=ttt.start)
    t_ttt.start()


if __name__ == "__main__":
    main()
