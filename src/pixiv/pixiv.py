import json
from typing import *

import pixivpy3

from utils.Illust import PixivIllust
from utils.basic_config import get_logger

logger = get_logger(__name__)

with open("token.json") as fp:
    _token = json.load(fp)

API = pixivpy3.AppPixivAPI()
API.auth(refresh_token=_token["pixiv"])

def get_agent() -> pixivpy3.AppPixivAPI:
    logger.info(f"Get Pixiv agent {API}")
    return API

def illust_bookmark_add(illust:Union[str, int, PixivIllust, Dict[str, Any]], restrict:str="public", userTags:Optional[List[str]]=None):
    logger.debug(f"Bookmark ({type(illust)}){illust}")
    if isinstance(illust, (str, int)):
        try:
            illust = API.illust_detail(illust)
        except pixivpy3.PixivError:
            logger.warning(f"Bookmark failed: Pixiv Error")
            return 
        else:
            illustId = illust["illust"]["id"]
            tags = [x["name"] for x in illust["illust"]["tags"]]
    elif isinstance(illust, PixivIllust):
        illustId = illust.id
        tags = (illust.userTags + illust.authTags)
    elif isinstance(illust, dict):
        illustId = illust["id"]
        tags = illust["authTags"].split(',') if isinstance(illust["authTags"], str) else illust["authTags"]
    else:
        raise ValueError(f"Param 'illust' type incorrect, should be one of str, int, PixivIllust and Dict[str, Any]")
    
    if userTags:
        tags = userTags + tags
    tags = tags[:10]
    logger.info(f"Bookmark {illustId} with {len(tags)} tags")
    res = API.illust_bookmark_add(illustId, restrict=restrict, tags=tags)
    logger.debug(f"Respose: {res}")
    return res