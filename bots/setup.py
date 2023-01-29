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
    "insta_ids" : {
        "freen": "233012029",
        "becky": "44813644697"
    },
}

glossary = {
    "พุง":"Belly",
    "น่ายัก":"cute",
    "ยัก":"love",
    "หมูแดง":"MuDaeng",
    "ง้อด้วย":"waiting for reconciliation",
    "งอน":"sulking"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()