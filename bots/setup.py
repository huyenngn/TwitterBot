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
        "คนรัก" : "คนที่รัก",
        "มามี้" : "mami",
        "ยัก" : "รัก", # yak -> rak
        "ฟรีน" : "Freen",
        "ง้อ" : "reconcile",
        "งอน" : "sulk",
        "สาม" : "แซม", # Sam
        "นุคน" : "เบ็คกี้",
        "นุ" : "เบ็คกี้",
        "หนู" : "เบ็คกี้",
        "พี่" : "ภคินี" # Phi -> sister
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()