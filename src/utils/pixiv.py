from traceback import format_exc
from typing import *

import pixivpy3
from pixivpy3.aapi import _RESTRICT as RESTRICT_TYPE
from pixivpy3.utils import PixivError

from utils import TOKEN
from utils.basic_config import get_logger
from utils.types import ILLUST_TYPE, Illust, SanityLevel

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

API: pixivpy3.AppPixivAPI = _PAPI()


# functions
def get_agent() -> pixivpy3.AppPixivAPI:
    return API

def refresh_token() -> None:
    API.auth()
    
class PixivIllust(Illust):
    region:str = "pixiv"
    @property
    def home(self) -> str:
        return f"https://www.pixiv.net/artworks/{self.id}"
    
    @classmethod
    def from_pixiv(cls, pixJson: Dict[str, Any], 
                 reverseProxy:str="i.pixiv.cat") -> None:
        """

        Args:
            pixJson (Dict[str, Any], optional): 从 illust_detail(.) 生成. Defaults to None.
            dbDict (Dict[str, str], optional): 从数据库生成. Defaults to None.
        """
        self = cls()
        if "illust" in pixJson:
            pixJson = pixJson["illust"]
        self.id = pixJson["id"]
        self.pageCount = pixJson["page_count"]
        self.title = pixJson["title"]
        self.author = pixJson["user"]["name"]
        self.authorId = pixJson["user"]["id"]
        if pixJson["x_restrict"] == 1:
            self.sanityLevel = SanityLevel.e
        else:
            self.sanityLevel = SanityLevel(pixJson["sanity_level"])
        url = pixJson["image_urls"]["large"]
        if reverseProxy:
            self.url = url.replace("i.pximg.net", reverseProxy)

        self.authTags = [x["name"] for x in pixJson["tags"]]
        # TODO: user tag
        self.userTags = []
        # TODO: ugoira
        self.type = pixJson["type"]
        return self
    
    def add_bookmark(self, restrict: RESTRICT_TYPE = "public", userTags: Optional[List[str]] = None) -> bool:
        """收藏pixiv illust（带tags）

        Args:
            restrict (str, optional):
                收藏到公开收藏夹(public)或私人收藏夹(private)。Defaults to "public".
            userTags (Optional[List[str]], optional): 
                自定义tags. Defaults to None.

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"Do bookmark {self}")
        illustId = self.id
        tags = (self.userTags + self.authTags)

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

    def illust_image_urls(self, reverseProxy:str|None="i.pixiv.cat") -> List[str]:
        """获取指定pixiv illust的所有页图片的链接

        Returns:
            List[str]: 
        """
        logger.info(f"Getting illust images for {self}")
        illust = API.illust_detail(self.id)
        if illust is not None:
            illust = illust["illust"]
        else:
            logger.error(f"Getting illust images for {self} error {format_exc()}")
            return None

        pageCount = illust["page_count"]
        if pageCount > 1:
            urls = [x["image_urls"]["large"] for x in illust["meta_pages"]]
        else:
            urls = [illust["image_urls"]["large"]]
        if reverseProxy:
            urls = [url.replace("i.pximg.net", reverseProxy) for url in urls]
        logger.debug(f"{self} {pageCount} pages: \n\t{urls}")
        return urls
    

def get_following_list() -> List[int]|None:
    """关注列表

    Returns:
        List[int]: 
    """
    logger.debug(f"get_following_list:")
    ids = []
    for restrict in ("public", "private"):
        offset = 0
        while True:
            result = API.user_following(API.user_id, restrict, offset)
            ids.extend(user['user']['id'] for user in result['user_previews'])
            next = API.parse_qs(result["next_url"])
            logger.debug(f"{len(ids)}, next:{next}")
            if next is None:
                break
            else:
                offset = next["offset"]
    logger.debug(f"get_following_list done: {len(ids)}")
    return ids
