from ntpath import join
from typing import *
from pixivpy3 import AppPixivAPI


_RATING: TypeAlias = Literal["u", "g", "s", "q", "e", ""]
_ILLUST_TYPE: TypeAlias = Literal["illust", "ugoira", ""]


# illust
class PixivIllust:
    id: int
    url: str
    pageCount: int
    authTags: List[str]
    userTags: List[str]
    rating: _RATING
    type: _ILLUST_TYPE
    title: str
    author: str
    authorId: int
    _INT_ATTR = ["id", "pageCount", "authorId"]
    _STRING_ATTR = ["url", "rating", "type", "title", "author"]
    _LIST_ATTR = ["authTags", "userTags"]

    def __init__(self, pixiv_agent:AppPixivAPI=None, id: int = None,
                 pixJson: Dict[str, Any] = None, dbDict:Dict[str, str]=None) -> None:
        super().__init__()
        assert id is not None or pixJson is not None or dbDict is not None
        self.agent = pixiv_agent
        if pixJson is not None or id is not None:
            # from pixiv
            if pixJson is not None:
                self.id = pixJson["id"]
            else:
                assert self.agent is not None
                self.id = id
                pixJson = self.agent.illust_detail(id)
                pixJson = pixJson["illust"]
            self.pageCount = pixJson["page_count"]
            self.title = pixJson["title"]
            self.author = pixJson["user"]["name"]
            self.authorId = pixJson["user"]["id"]
            url = pixJson["image_urls"]["large"]
            self.url = url.replace("i.pximg.net", "i.pixiv.cat")

            self.authTags = [x["name"] for x in pixJson["tags"]]
            # TODO: user tag
            self.userTags = []
            # TODO: rating
            self.rating = 'e' if pixJson["x_restrict"] == 1 else 'u'
            # TODO: ugoira
            self.type = pixJson["type"]
        elif dbDict is not None:
            # from db
            for key in PixivIllust._STRING_ATTR:
                self.__setattr__(key, dbDict[key])
            for key in PixivIllust._INT_ATTR:
                self.__setattr__(key, int(dbDict[key]))
            for key in PixivIllust._LIST_ATTR:
                self.__setattr__(key, dbDict[key].split(','))

    def dump(self) -> Dict[str, str]:
        data = {}
        for key in PixivIllust._STRING_ATTR:
            data[key] = self.__getattribute__(key)
        for key in PixivIllust._INT_ATTR:
            data[key] = str(self.__getattribute__(key))
        for key in PixivIllust._LIST_ATTR:
            data[key] = ','.join(self.__getattribute__(key))
        return data