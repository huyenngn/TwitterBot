import logging

settings = {
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
    "insta_handles" : {
        "freen": "233012029",
        "becky": "44813644697"
    },
}

glossary = {
    "อะะ" : " ahh",
    "ยัก" : "รัก",
    "ฟรีน" : " Freen",
    "ง้อ" : " reconcile",
    "สาม" : " Sam",
    "นุ" : "หนู",
    "หนู" : " Nu",
    "ด้วย" : " please"
}

corrections = {
    "#" : "#.",
    "older brother" : "Phi",
    "nuke" : "Nu"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()