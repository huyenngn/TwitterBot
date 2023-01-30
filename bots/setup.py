import logging

bot_settings = {
    "biases" : ["freen", "becky"],
    "admins" : ["srchafreen", "AngelssBecky"],
    "twitter_handles" : {
        "freen": "srchafreen",
        "becky": "AngelssBecky",
        "nam": "namorntaraaa",
        "gap": "GAPtheseries"
    },
    "emojis" : {
        "freen":  "\ud83d\udc30",
        "becky": "\ud83e\udda6",
        "nam": "\ud83d\udea2",
        "gap": "\ud83d\udc69\ud83c\udffb\u200d\u2764\ufe0f\u200d\ud83d\udc8b\u200d\ud83d\udc69\ud83c\udffb",
    },
}

translation_settings = {
    "src" : "th",
    "dst" : "en",
    # Replacements applied before translating
    "glossary" : {
        "อะะ" : " ahh",
        "คนรัก" : "คนที่รัก",   # people who love
        "มามี้" : "mami",
        "ยัก" : "รัก",        # yak
        "ฟรีน" : "ไมเคิล",    # Freen -> Michael
        "ง้อ" : "reconcile", # reconcile ->
        "งอน" : "sulk",     # sulk ->
        "สาม" : "มาเรีย",     # Sam -> Maria
        "นุคน" : "แซนดร้า",   # Nu -> Sandra
        "นุ" : "แซนดร้า",
        "หนู" : "แซนดร้า",
        "พี่" : "ภคินี",        # Phi
        "ยัง" : ""           # still/yet
    },
    "corrections" : {
        "#" : "#.",
        "Michael" : "Freen",
        "Sandra" : "Nu",
        "Maria" : "Sam"
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()