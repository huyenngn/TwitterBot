import threading
# from bots.instagram_updates import InstagramUpdatesBot
from bots.translate_tweets import TranslateTweetsBot


def main():
    ttb = TranslateTweetsBot()
    rules = ttb.create_rules()
    ttb.delete_all_rules()
    ttb.set_rules(rules)
    t_ttb = threading.Thread(target=ttb.start)
    t_ttb.start()

    # api = ttb.get_api()
    # iub = InstagramUpdatesBot(api=api)
    # t_iub = threading.Thread(target=iub.start)
    # t_iub.start()


if __name__ == "__main__":
    main()
