from traceback import format_exc
from typing import *

from filters import FilterBase, UniqueFilter
from utils.pixiv import API as papi
from utils.pixiv import PixivIllust

from . import logger
from .base import GrabberBase


class PixivGrabBase(GrabberBase):
    def __init__(self, num: int = 60, filters: Iterable[FilterBase] = []) -> None:
        super().__init__(num=num, filters=[UniqueFilter()]+filters)

class PixivRecommendedGrab(PixivGrabBase):
    """抓取 pixiv 推荐
    """
    def source(self) -> List[PixivIllust]:
        logger.info("Getting pixiv recommended ...")
        try:
            recommended = papi.illust_recommended()
            assert recommended is not None
            recommended = recommended["illusts"]
        except (KeyError, AssertionError):
            logger.warning(f"Pixiv Grab Error: {format_exc()}, skip")
            return []
        
        result = [PixivIllust.from_pixiv(pixJson=illust) for illust in recommended]
        return result

# class PixivFollowGrab(PixivGrabBase):
#     """抓取关注
#     """
#     def __init__(self, restrict:List[str]=["public"], filters: Iterable[FilterBase] = []) -> None:
#         super().__init__(num=-1, filters=filters)
#         self.restrict = restrict
        
#     def source(self) -> List[Illust]:
#         logger.info("Getting pixiv follow ...")
#         try:
#             followIllusts = []
#             for r in self.restrict:
#                 followIllusts.extend(self.papi.illust_follow(r)["illusts"])
#         except (PixivError, KeyError):
#             logger.warning("Pixiv Error, skip")
#             return []
        
#         result = [Illust(self.papi, pixJson=illust) for illust in followIllusts]
#         return result
