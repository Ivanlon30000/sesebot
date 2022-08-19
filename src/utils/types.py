"""
基础类

SanityLevel:
枚举类型。内容评级

Illust:
抽象类。
用于为所有模块(bot, grab, push, db)提供一个统一的操作 setu 的接口
"""

from typing import *
from enum import Enum
from abc import ABC, abstractmethod

# interfaces
class Dumpable(ABC):
    @property
    @classmethod
    def _INT_ATTR(cls) -> Iterable[str]:
        return []
    
    @property
    @classmethod
    def _STRING_ATTR(cls) -> Iterable[str]:
        return []
    
    @property
    @classmethod
    def _LIST_ATTR(cls) -> Iterable[str]:
        return []
    
    def load(self, dbDict:Dict[str, str]) -> None:
        for key in self._STRING_ATTR:
            self.__setattr__(key, dbDict[key])
        for key in self._INT_ATTR:
            self.__setattr__(key, int(dbDict[key]))
        for key in self._LIST_ATTR:
            self.__setattr__(key, dbDict[key].split(','))
    
    def dump(self) -> Dict[str, str|int]:
        data = {}
        for key in self._STRING_ATTR:
            data[key] = self.__getattribute__(key)
        for key in self._INT_ATTR:
            data[key] = self.__getattribute__(key)
        for key in self._LIST_ATTR:
            data[key] = ','.join(self.__getattribute__(key))
        return data
    
    @classmethod
    def from_db(cls, dbDict:Dict[str,str]):
        self = cls()
        self.load(dbDict)
        return self

# types
class SanityLevel(Enum):
    UNKNOWN = u = 0
    GENERAL = g = 2
    SENSITIVE = s = 4
    QUESTIONALBE = q = 6
    EXPLICIT = e = 8
    
ILLUST_TYPE: TypeAlias = Literal["illust", "ugoira", "video"]

class Illust(Dumpable):
    id: int
    url: str
    pageCount: int
    authTags: List[str]
    userTags: List[str]
    type: ILLUST_TYPE
    title: str
    author: str
    authorId: str
    sanityLevel: int
    home: str
    region = "unknown"
    
    @property
    def _INT_ATTR(cls) -> Iterable[str]:
        return {"id", "pageCount", "sanityLevel"}
    
    @property
    def _STRING_ATTR(cls) -> Iterable[str]:
        return {"url", "type", "title", "author", "authorId"}
    
    @property
    def _LIST_ATTR(cls) -> Iterable[str]:
        return {"authTags", "userTags"}
    
    def __repr__(self) -> str:
        return f"<Illust: {self.id}, region: {self.region}, title: {self.title}>"
    
    def load(self, dbDict:Dict[str, str]) -> None:
        for key in self._STRING_ATTR:
            self.__setattr__(key, dbDict[key])
        for key in self._INT_ATTR:
            self.__setattr__(key, int(dbDict[key]))
        for key in self._LIST_ATTR:
            self.__setattr__(key, dbDict[key].split(','))
    
    def dump(self) -> Dict[str, str|int]:
        data = {}
        for key in self._STRING_ATTR:
            data[key] = self.__getattribute__(key)
        for key in self._INT_ATTR:
            data[key] = self.__getattribute__(key)
        for key in self._LIST_ATTR:
            data[key] = ','.join(self.__getattribute__(key))
        return data
    
    @abstractmethod
    def add_bookmark(self, **kwargs) -> bool:
        """添加到收藏

        Returns:
            bool: 操作是否成功
        """ 
        raise NotImplementedError()
    
    @abstractmethod
    def illust_image_urls(self, **kwargs) -> List[str]:
        """获取illust包含的所有图片的链接

        Returns:
            List[str]: 
        """
        raise NotImplementedError()