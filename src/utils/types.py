from typing import *
from enum import Enum
from abc import ABC, abstractmethod, abstractproperty

# types
class SanityLevel(Enum):
    UNKNOWN = u = 0
    GENERAL = g = 2
    SENSITIVE = s = 4
    QUESTIONALBE = q = 6
    EXPLICIT = e = 8
    
ILLUST_TYPE: TypeAlias = Literal["illust", "ugoira", "video"]

class Illust(ABC):
    id: int
    url: str
    pageCount: int
    authTags: List[str]
    userTags: List[str]
    type: ILLUST_TYPE
    title: str
    author: str
    authorId: str
    sanityLevel: SanityLevel
    home: str
    region = "unknown"
    _INT_ATTR = {"id", "pageCount", "sanityLevel"}
    _STRING_ATTR = {"url", "type", "title", "author", "authorId"}
    _LIST_ATTR = {"authTags", "userTags"}
    
    def __repr__(self) -> str:
        return f"<Illust: {self.id}, region: {self.region}, title: {self.title}>"
    
    def load(self, dbDict:Dict[str, str]) -> None:
        for key in self._STRING_ATTR:
            self.__setattr__(key, dbDict[key])
        for key in self._INT_ATTR:
            self.__setattr__(key, int(dbDict[key]))
        for key in self._LIST_ATTR:
            self.__setattr__(key, dbDict[key].split(','))
    
    def dump(self) -> Dict[str, str]:
        data = {}
        for key in self._STRING_ATTR:
            data[key] = self.__getattribute__(key)
        for key in self._INT_ATTR:
            data[key] = str(self.__getattribute__(key))
        for key in self._LIST_ATTR:
            data[key] = ','.join(self.__getattribute__(key))
        return data
    
    @classmethod
    def from_db(cls, dbDict:Dict[str,str]):
        self = cls()
        self.load(dbDict)
        return self
    
    @abstractmethod
    def add_bookmark(self, **kwargs) -> bool:
        """添加到收藏

        Returns:
            bool: 操作是否成功
        """ 
        pass
    
    @abstractmethod
    def illust_image_urls(self, **kwargs) -> List[str]:
        """获取illust包含的所有图片的链接

        Returns:
            List[str]: 
        """
        pass