import json
import os

# print(os.listdir('/config'))
try:
    with open("/config/config.json") as fp:
        CONFIG = json.load(fp)
except FileNotFoundError:
    with open("config/config.json") as fp:
        CONFIG = json.load(fp)

try:
    with open("/config/token.json") as fp:
        TOKEN = json.load(fp)
except FileNotFoundError:
    with open("config/token.json") as fp:
        TOKEN = json.load(fp)

ME = TOKEN["chatid_me"]