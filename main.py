import threading
from bots.translate_tweets import TranslateTweetsBot

bot_settings = {
    # twitter user the bot will automatically interact with
    "biases": ["srchafreen", "AngelssBecky"],
    # test users and admins
    "admins": ["FreenBeckyBot", "joohwangblink"],
    # twitter users and their respective emoji/alias
    # this could be accounts your biases regularily interact with
    # (including your biases)
    "twitter_handles": {
        "srchafreen": "\ud83d\udc30",
        "AngelssBecky": "\ud83e\udda6",
        "namorntaraaa": "\ud83d\udea2",
        "GAPtheseries": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
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
    ttb = TranslateTweetsBot(
        biases=bot_settings["biases"],
        src=translation_settings["src"],
        dst=translation_settings["dst"],
        glossary=translation_settings["glossary"],
        corrections=translation_settings["corrections"],
        admins=bot_settings["admins"],
        handles=bot_settings["twitter_handles"]
        )
    # ttb.tl.translate_image("https://pbs.twimg.com/media/FO3yZeYVsAEfBJx?format=jpg&name=large")
    # rules = ttb.create_rules()
    # ttb.delete_all_rules()
    # ttb.set_rules(rules)
    t_ttb = threading.Thread(target=ttb.start)
    t_ttb.start()
    # api = ttb.get_api()


if __name__ == "__main__":
    main()
