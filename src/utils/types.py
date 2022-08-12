from typing import *
from enum import Enum

# types
class SanityLevel(Enum):
    UNKNOWN = u = 0
    GENERAL = g = 2
    SENSITIVE = s = 4
    QUESTIONALBE = q = 6
    EXPLICIT = e = 8
    
_ILLUST_TYPE: TypeAlias = Literal["illust", "ugoira", "video"]

class Illust:
    id: int
    url: str
    pageCount: int
    authTags: List[str]
    userTags: List[str]
    type: _ILLUST_TYPE
    title: str
    author: str
    authorId: str
    sanityLevel: SanityLevel
    region: str
    
    def __init__(self) -> None:
        self._INT_ATTR = {"id", "pageCount", "sanityLevel"}
        self._STRING_ATTR = {"url", "type", "title", "author", "region", "authorId"}
        self._LIST_ATTR = {"authTags", "userTags"}
        self.region = "unknown"
    
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
    
    @classmethod
    def from_pixiv(cls, pixJson: Dict[str, Any], 
                 reverseProxy:str="i.pixiv.cat") -> None:
        """

        Args:
            pixJson (Dict[str, Any], optional): 从 illust_detail(.) 生成. Defaults to None.
            dbDict (Dict[str, str], optional): 从数据库生成. Defaults to None.
        """
        self = cls()
        self.region = "pixiv"
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