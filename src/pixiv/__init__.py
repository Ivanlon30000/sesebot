import json

import pixivpy3
from utils import TOKEN

# init agent
API = pixivpy3.AppPixivAPI()
API.auth(refresh_token=TOKEN["pixiv"])


# functions
def get_agent() -> pixivpy3.AppPixivAPI:
    logger.info(f"Get Pixiv agent {API}")
    return API

def refresh_token() -> None:
    logger.info("Refresh token")
    res = API.auth(refresh_token=TOKEN["pixiv"])
    logger.debug(res)

# imports
from .aapi import *
from .types import *
