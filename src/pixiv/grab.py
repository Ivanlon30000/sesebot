from typing import *
from . import PixivIllust
from abc import ABC, abstractmethod
from utils.basic_config import get_logger
from traceback import format_exc
import time
from pixivpy3.utils import PixivError

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
    def __init__(self, db) -> None:
        self.db = db
        
    def filter(self, illusts: List[PixivIllust], **kwargs) -> List[PixivIllust]:
        existIllust = set(x.split(':')[-1] for x in self.db.keys("illust:*"))
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
    def __init__(self, db, num:int=60, expire:int=86400, 
                 interval:Optional[int]=None, errInterval:Optional[int]=None,                 
                 filters:Union[Iterable[IllustFilter], IllustFilter]=_defaultFilter,
                 extraFilters: Union[Iterable[IllustFilter], IllustFilter]=[]) -> None:
        """用于抓取图片

        Args:
            db: redis database
            num (int, optional): 每次最大拉去数量. Defaults to 60.
            expire (int, optional): 过期时间/秒. Defaults to 86400.
            interval (Optional[int], optional): 仅自动抓取有效，执行抓取间隔/秒. Defaults to None.
            errInterval (Optional[int], optional): 仅自动抓取有效，抓取错误时的检测/秒. Defaults to None.
            filters (Union[Iterable[IllustFilter], IllustFilter], optional): 过滤器. Defaults to allpass_filter.
        """
        self.db = db
        self.maxNum = num
        self.expireTime = expire
        self.interval = interval
        self.errInterval = errInterval
        self.filters = (filters if isinstance(filters, Iterable) else [filters]) + extraFilters
    
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
        
        for filter in self.filters:
            illusts = filter(illusts)
        
        for illust in illusts:
            key = "illust:{}".format(illust.id)
            self.db.hset(key, mapping=illust.toDict())
            if self.expireTime is not None:
                self.db.expire(key, self.expireTime)
        logger.debug(f"Added {[x.id for x in illusts]}")
        logger.info(f"Grab done: {len(illusts)} illusts")
        return illusts
                
    def run(self) -> None:
        """阻塞式自动抓取
        """
        assert self.interval is not None
        while True:
            result = self.grab()
            sleepTime = self.errInterval if self.errInterval is not None and result is None else self.interval
            logger.info(f"Sleep for {sleepTime}s")
            time.sleep(sleepTime)


class PixivRecommendedGrab(GrabBase):
    """抓取 pixiv 推荐
    """
    def __init__(self, db, papi, num: int = 60, expire: int = 86400,
                 interval: Optional[int] = None, errInterval: Optional[int] = None,
                 filters: Union[Iterable[IllustFilter], IllustFilter] = _defaultFilter,
                 extraFilters: Union[Iterable[IllustFilter], IllustFilter]=[]) -> None:
        super().__init__(db, num, expire, interval, errInterval, filters, extraFilters)
        self.papi = papi
        
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