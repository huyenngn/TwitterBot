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
        "คนรัก" : "คนที่รัก",
        "มามี้" : "สมศักดิ์",     # Mami -> Somsak
        "ยัก" : "รัก",        # yak
        "ฟรีนกี้" : "เจค",      # Freenky -> Jake
        "ฟรีน" : "อัมพร",   # Freen -> Amporn
        "สาม" : "แซม",        # Sam 
        "นุคน" : "หนู",   # Nu -> Sandra
        "นุ" : "หนู",
        "หนู" : "แซนดร้า",
        "น้องพุง" : "สมชาย",     # Nong Belly -> Somchai
        "น้อง" : "Nong",       # Nong
        "พี่" : "Phi",       # Phi
        "ยัง" : "",           # still/yet
    },
    # replacements applied after translating
    "corrections" : {
        "#" : "#.",
        "Amporn" : "Freen",
        "Jake" : "Freenky",
        "Sandra" : "Nu",
        "Somsak" : "Mami",
        "Somchai" : "Nong Belly",
        "I am" : "",
        "I'm " : "",
        "I " : "",
        " me " : " me/you ",
        " me." : " me/you.",
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()