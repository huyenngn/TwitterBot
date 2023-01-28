import logging
import threading
# from instagram import Instagram_Reposter
from twitter import Twitter_Interacter

settings = {
    "biases" : ["freen", "becky"],
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
        "freen": "srchafreen",
        "becky": "AngelssBecky"
    },
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def main():
    ti = Twitter_Interacter()
    api = ti.get_api()
    rules = ti.create_rules()
    ti.delete_all_rules()
    ti.set_rules(rules)
    t_twitter = threading.Thread(target=ti.start)
    t_twitter.start()
    
    # ir = Instagram_Reposter(api=api)
    # t_insta = threading.Thread(target=ir.start)
    # t_insta.start()

if __name__ == "__main__":
    main()