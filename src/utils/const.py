import json

# load config
with open("config.json") as fp:
    CONFIG = json.load(fp)
    
with open("token.json") as fp:
    TOKEN = json.load(fp)

ME = TOKEN["chatid_me"]