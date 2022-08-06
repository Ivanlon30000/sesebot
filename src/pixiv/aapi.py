from typing import *

import pixivpy3
from pixivpy3.utils import PixivError
from utils.basic_config import get_logger
from traceback import format_exc, format_exc

from . import API
from .types import PixivIllust

logger = get_logger(__name__)


def illust_bookmark_add(illust: Union[str, int, PixivIllust, Dict[str, Any]],
                        restrict: str = "public",
                        userTags: Optional[List[str]] = None) -> Dict[str, Any]:
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
        raise ValueError(
            f"Param 'illust' type incorrect, should be one of str, int, PixivIllust and Dict[str, Any]")

    if userTags:
        tags = userTags + tags
    tags = tags[:10]
    logger.info(f"Bookmark {illustId} with {len(tags)} tags")
    res = API.illust_bookmark_add(illustId, restrict=restrict, tags=tags)
    logger.debug(f"Respose: {res}")
    return res

def illust_image_urls(iid:int) -> List[str]:
    logger.info(f"Getting illust images for {iid}")
    try:
        illust = API.illust_detail(iid)["illust"]
    except (PixivError, KeyError):
        logger.error(f"Getting illust images for {iid} error {format_exc()}")
        return None

    pageCount = illust["page_count"]
    if pageCount > 1:
        urls = [x["image_urls"]["large"].replace("i.pximg.net", "i.pixiv.cat") for x in illust["meta_pages"]]
    else:
        urls = [illust["image_urls"]["large"]]
    logger.info(f"{pageCount} pages: {urls}")
    return urls
    