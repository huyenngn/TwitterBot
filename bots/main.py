from twitter import *
import os

DEBUG = True

FREEN_TWT = "srchafreen"
BECKY_TWT = "AngelssBecky"

if DEBUG:
    rules = [
    {"value": 'from:joohwangblink -is:retweet', "tag": "debug"}
    ]
else:
    rules = [
    {"value": 'to:'+FREEN_TWT+' is:verified!', "tag": "freen_reply"},
    {"value": 'to:'+BECKY_TWT+' is:verified', "tag": "becky_reply"},
    {"value": 'from:'+FREEN_TWT+' -is:retweet', "tag": "freen"},
    {"value": 'from:'+BECKY_TWT+' -is:retweet', "tag": "becky"}
    ]

def main():
    # rules = twt.get_rules()
    ta = Client()
    ta.delete_all_rules()
    ta.set_rules(rules)
    ta.get_stream()


if __name__ == "__main__":
    main()