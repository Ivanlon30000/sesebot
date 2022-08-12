from enum import Enum
import logging
import os
from traceback import format_exc
from typing import *

import pixivpy3
from pixivpy3.aapi import _RESTRICT
from pixivpy3.utils import PixivError

from utils import TOKEN
from utils.basic_config import get_logger
from utils.db import get_illust
from utils.types import Illust


logger = get_logger(__name__)

_papi = pixivpy3.AppPixivAPI()

class _PAPI:
    api: pixivpy3.AppPixivAPI
    auth: Callable
    maxTry: int
    
    def __init__(self) -> None:
        self.auth()
        
    def __getattribute__(self, name: str) -> Any:
        # self own attri
        # print(name)
        selfattri = {
            "api": _papi,
            "auth": lambda refresh_token=None: _papi.auth(refresh_token=TOKEN["pixiv"] if refresh_token is None else refresh_token),
            "maxTry": 3,
        }
        if name in selfattri:
            return selfattri[name]
        
        # papi attri
        attri = _papi.__getattribute__(name)

        if isinstance(attri, Callable):
            def wraper(*args, **kwargs) -> Any:
                for _ in range(self.maxTry):
                    # try self.maxTry times. If raise PixivError or error in response, do auth then retry
                    flag = True
                    try:
                        result = attri(*args, **kwargs)
                        logger.debug(f"\n\tAAPI calls {name}(*{args}, **{kwargs}):\n\treturns {result}")
                    except PixivError:
                        flag = False
                    else:
                        if isinstance(result, dict) and "error" in result:
                            flag = False
                    
                    if flag:
                        return result
                    else:
                        self.api.auth()
                return None
            return wraper
        else:
            return attri

API: pixivpy3.AppPixivAPI = _PAPI() if os.environ.get("DEVELOP", False) else _papi


# functions
def get_agent() -> pixivpy3.AppPixivAPI:
    return API

def refresh_token() -> None:
    API.auth()

def add_bookmark(illust: Union[str, int, Illust],
                        restrict: _RESTRICT = "public",
                        userTags: Optional[List[str]] = None) -> bool:
    """收藏pixiv illust（带tags）

    Args:
        illust (Union[str, int, PixivIllust]): 
            可以是id(int|str)（查收数据库 or tags在线获取）或types.Illust（tags本地读取）。
        restrict (str, optional):
            收藏到公开收藏夹(public)或私人收藏夹(private)。Defaults to "public".
        userTags (Optional[List[str]], optional): 
            自定义tags. Defaults to None.

    Returns:
        bool: 操作是否成功
    """
    logger.info(f"Bookmark ({type(illust)}){illust}")
    if isinstance(illust, (str, int)):
        try:
            illustId = illust
            illust = get_illust(illustId)
            if illust is None:
                illust = API.illust_detail(illustId)
                assert illust is not None, "aapi returns None"
                illust = Illust.from_pixiv(illust)
        except:
            logger.error(f"Bookmark error {format_exc()}")
            return False
    elif isinstance(illust, Illust):
        pass
    else:
        raise ValueError(
            f"Param 'illust' type incorrect, should be one of str, int, Illust ")
    
    illustId = illust.id
    tags = (illust.userTags + illust.authTags)

    if userTags:
        tags = userTags + tags
    if len(tags) > 10:
        logger.warning(f"Bookmark {illustId} tags exceed max number, tags after 10th lost.")
        tags = tags[:10]
    logger.info(f"Bookmark {illustId} with {len(tags)} tags")
    res = API.illust_bookmark_add(illustId, restrict=restrict, tags=tags)
    if res is None:
        logger.warning(f"Add bookmark {illustId} failed.")
        return False
    return True

def illust_image_urls(illustId:int|str) -> List[str]:
    """获取指定pixiv illust的所有页图片的链接

    Args:
        illustId (int | str): 

    Returns:
        List[str]: 
    """
    logger.info(f"Getting illust images for {illustId}")
    illust = API.illust_detail(illustId)
    if illust is not None:
        illust = illust["illust"]
    else:
        logger.error(f"Getting illust images for {illustId} error {format_exc()}")
        return None

    pageCount = illust["page_count"]
    if pageCount > 1:
        urls = [x["image_urls"]["large"].replace("i.pximg.net", "i.pixiv.cat") for x in illust["meta_pages"]]
    else:
        urls = [illust["image_urls"]["large"]]
    logger.info(f"{pageCount} pages: {urls}")
    return urls
    