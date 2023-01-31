import logging

bot_settings = {
    # twitter user the bot will automatically interact with
    "biases" : ["srchafreen", "AngelssBecky"],
    # test users and admins (excluding the bots account)
    "admins" : ["srchafreen", "AngelssBecky"],
    # twitter users and their respective emoji/alias
    # this could be accounts your biases regularily interact with
    # (including your biases)
    "twitter_handles" : {
        "srchafreen":  "\ud83d\udc30",
        "AngelssBecky": "\ud83e\udda6",
        "namorntaraaa": "\ud83d\udea2",
        "GAPtheseries": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
    },
}

translation_settings = {
    # language settings
    "src" : "th",
    "dst" : "en",
    # replacements applied before translating
    "glossary" : {
        "อะะ" : " ahh",
        "คนรัก" : "คนที่รัก",   # people who love
        "มามี้" : "ไมเคิล",     # Mami -> Michael
        "ยัก" : "รัก",        # yak
        "ฟรีนกี้" : "มิแรนด้า",    # Freenky -> Miranda
        "สาม" : "มาเรีย",     # Sam -> Maria
        "นุคน" : "แซนดร้า",   # Nu -> Sandra
        "นุ" : "แซนดร้า",
        "หนู" : "แซนดร้า",
        "พี" : "พี่สาว",
        "ยัง" : "",           # still/yet
    },
    # replacements applied after translating
    "corrections" : {
        "#" : "#.",
        "Miranda" : "Freenky",
        "Sandra" : "Nu",
        "Maria" : "Sam",
        "Michael" : "Mami",
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()