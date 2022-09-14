import os
import yaml

# print(os.listdir('/config'))
try:
    with open("/config/config.yaml") as fp:
        CONFIG = yaml.full_load(fp)
except FileNotFoundError:
    with open("config/config.yaml") as fp:
        CONFIG = yaml.full_load(fp)

try:
    with open("/config/token.yaml") as fp:
        TOKEN = yaml.full_load(fp)
except FileNotFoundError:
    with open("config/token.yaml") as fp:
        TOKEN = yaml.full_load(fp)

ME = TOKEN["me"]