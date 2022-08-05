import json
import pixivpy3

with open("token.json") as fp:
    _token = json.load(fp)

# init agent
API = pixivpy3.AppPixivAPI()
API.auth(refresh_token=_token["pixiv"])


# functions
def get_agent() -> pixivpy3.AppPixivAPI:
    logger.info(f"Get Pixiv agent {API}")
    return API

# imports
from .aapi import *
from .types import *