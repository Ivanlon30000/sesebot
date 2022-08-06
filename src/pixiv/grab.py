from typing import *
from . import PixivIllust
from abc import ABC, abstractmethod
from utils.basic_config import get_logger
from traceback import format_exc
import time
from pixivpy3.utils import PixivError
from pixivpy3 import AppPixivAPI
from redis import Redis

# basic
logger = get_logger(__name__)


# type alias
IllustFilter = Callable[[List[PixivIllust]], List[PixivIllust]]


# filters
class FilterBase:
    def condition(self, illust:PixivIllust) -> bool:
        return True

    def filter(self, illusts:List[PixivIllust], **kwargs) -> List[PixivIllust]:
        return [illust for illust in illusts if self.condition(illust)]

    def __call__(self, illusts:List[PixivIllust], **kwargs) -> List[PixivIllust]:
        return self.filter(illusts, **kwargs)

class AllpassFilter(FilterBase):
    pass

class UniqueFilter(FilterBase):
    def __init__(self, db:Redis, group="illust") -> None:
        self.db = db
        self.group = group
        
    def filter(self, illusts: List[PixivIllust], **kwargs) -> List[PixivIllust]:
        existIllust = set(x.split(':')[-1] for x in self.db.keys(f"{self.group}:*"))
        return [illust for illust in illusts if str(illust.id) not in existIllust]

class TagsFilter(FilterBase):
    def __init__(self, hasTags:Union[str,Iterable[str]]=[], noTags:Union[str,Iterable[str]]=[]) -> None:
        super().__init__()
        self.whitelist = [hasTags] if isinstance(hasTags, str) else hasTags
        self.blacklist = [noTags] if isinstance(hasTags, str) else noTags
        
    def condition(self, illust: PixivIllust) -> bool:
        tags = set(illust["authTags"])
        if len(self.blacklist) == 0 or all(x not in tags for x in self.blacklist):
            return self.whitelist == 0 or all(x in tags for x in self.whitelist)
        else:
            return False
    
_defaultFilter = [AllpassFilter()]


# grabs
class GrabBase(ABC):
    """Grab 基类
    """
    def __init__(self, db:Redis, num:int=60, expire:Optional[int]=86400, group:str="illust",        
                 filters:Iterable[IllustFilter]=_defaultFilter) -> None:
        """用于抓取图片

        Args:
            db: redis database
            num (int, optional): 每次最大拉去数量. Defaults to 60.
            expire (int, optional): 过期时间/秒. Defaults to 86400.
            filters (Union[Iterable[IllustFilter], IllustFilter], optional): 过滤器. Defaults to allpass_filter.
        """
        self.db = db
        self.maxNum = num
        self.group = group
        self.expireTime = expire
        self.filters = filters
    
    @abstractmethod
    def source(self) -> List[PixivIllust]:
        """抓取源
        """
        pass
    
    def grab(self) -> Optional[List[PixivIllust]]:
        """从源获取图片 -> 应用过滤器 -> 存入数据库
        """
        logger.info(f"{self.__module__} starts grabbing")
        try:
            illusts = self.source()[:self.maxNum]
            logger.info(f"Source {len(illusts)} illusts")
        except:
            logger.error(f"Grab error:\n{format_exc()}")
            return 
        
        logger.debug(self.filters)
        for filter in self.filters:
            logger.info(f"Apply {filter.__class__.__name__}")
            illusts = filter(illusts)
        
        for illust in illusts:
            key = "{}:{}".format(self.group, illust.id)
            self.db.hset(key, mapping=illust.toDict())
            if self.expireTime is not None:
                self.db.expire(key, self.expireTime)
        logger.debug(f"Added {[x.id for x in illusts]}")
        logger.info(f"Grab done: {len(illusts)} illusts")
        return illusts
                
    def run(self, interval:int=3600, errInterval:Optional[int]=30) -> None:
        """阻塞式自动抓取
        """
        while True:
            result = self.grab()
            sleepTime = errInterval if errInterval is not None and result is None else interval
            logger.info(f"Sleep for {sleepTime}s")
            time.sleep(sleepTime)

class PixivGrabBase(GrabBase):
    def __init__(self, db: Redis, papi:AppPixivAPI, num: int = 60, expire: Optional[int] = 86400, group: str = "illust",
                 filters: Iterable[IllustFilter] = []) -> None:
        super().__init__(db, num=num, expire=expire, group=group, filters=[UniqueFilter(db, group)]+filters)
        self.papi = papi

class PixivRecommendedGrab(PixivGrabBase):
    """抓取 pixiv 推荐
    """
    def source(self) -> List[PixivIllust]:
        logger.info("Getting pixiv recommended ...")
        try:
            recommended = self.papi.illust_recommended()
            recommended = recommended["illusts"]
        except (PixivError, KeyError):
            logger.warning("Pixiv Error, skip")
            return []
        
        result = [PixivIllust(self.papi, illust=illust) for illust in recommended]
        return result

class PixivFollowGrab(PixivGrabBase):
    """抓取关注
    """
    def __init__(self, db: Redis, papi: AppPixivAPI, restrict:List[str]=["public"], num:int=-1, expire: Optional[int] = 86400,
                 filters: Iterable[IllustFilter] = []) -> None:
        super().__init__(db, papi, num=num, expire=expire, group="follow", filters=filters)
        self.restrict = restrict
        
    def source(self) -> List[PixivIllust]:
        logger.info("Getting pixiv follow ...")
        try:
            followIllusts = []
            for r in self.restrict:
                followIllusts.extend(self.papi.illust_follow(r)["illusts"])
        except (PixivError, KeyError):
            logger.warning("Pixiv Error, skip")
            return []
        
        result = [PixivIllust(self.papi, illust=illust) for illust in followIllusts]
        return result