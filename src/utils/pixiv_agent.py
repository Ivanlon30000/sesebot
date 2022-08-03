import json
from typing import *

import pixivpy3

with open("token.json") as fp:
    _token = json.load(fp)

def get_agent() -> pixivpy3.AppPixivAPI:
    api = pixivpy3.AppPixivAPI()
    api.auth(refresh_token=_token["pixiv"])
    return api