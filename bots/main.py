import threading
from instagram import Instagram_Reposter
from twitter import Twitter_Interacter

def main():
    ti = Twitter_Interacter()
    api = ti.get_api()
    rules = ti.create_rules()
    ti.delete_all_rules()
    ti.set_rules(rules)
    t_twitter = threading.Thread(target=ti.start)
    t_twitter.start()
    
    ir = Instagram_Reposter(api=api)
    t_insta = threading.Thread(target=ir.start)
    t_insta.start()

if __name__ == "__main__":
    main()