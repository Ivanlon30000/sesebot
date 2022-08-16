"""
Grabber 基类

抽象类

添加新的Grabber只需要继承 GrabberBase 并实现 source() 方法，
sourece() 方法：返回 utils.types.Illust 的子类的列表，是抓取到的图片
参考：grabbers.pixiv.PixivRecommendedGrab
"""

import time
from abc import ABC, abstractmethod
from traceback import format_exc
from typing import *

from filters import FilterBase, _defaultFilters
from utils.db import add_illust
from utils.types import Illust

from . import logger


# grabs
class GrabberBase(ABC):
    def __init__(self, num:int, filters:Iterable[FilterBase]=_defaultFilters, expire:int|None=None) -> None:
        self.maxNum = num
        self.filters = filters
        self.expire = expire
    
    @abstractmethod
    def source(self) -> List[Illust]:
        """抓取源
        """
        raise NotImplementedError()
    
    def grab(self) -> Optional[List[Illust]]:
        """从源获取图片 -> 应用过滤器 -> 存入数据库
        """
        logger.info(f"{self.__class__.__name__} starts grabbing")
        try:
            illusts = self.source()[:self.maxNum]
            logger.info(f"Source {len(illusts)} illusts")
        except:
            logger.error(f"Grab error:\n{format_exc()}")
            return 
        
        for filter in self.filters:
            illusts = filter(illusts)
        
        for illust in illusts:
            res = add_illust(illust, expire=self.expire)
            if res is None:
                logger.warning(f"{illust} add to db error.")

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

