import base64
import json
import os
import time
from io import BytesIO
from typing import *

from .enums import *


# illust
class PixivIllust:
    id: int
    fp: Union[BytesIO, str]
    filesize: int
    authTags: List[str]
    userTags: List[str]
    rating: Rating
    type: IllustType
    title: str
    size: Tuple[int, int]
    createdTime: int

    def __init__(self, pixiv_agent, id: int = None, illust: Dict = None, 
                 rawdir: str = None, size: IllustSize = IllustSize.LARGE,
                 mode: str="") -> None:
        assert id is not None or illust is not None
        self.agent = pixiv_agent
        if illust is not None:
            self.id = illust["id"]
        else:
            self.id = id
            illust = self.agent.illust_detail(id)
            illust = illust["illust"]

        if rawdir is not None:
            os.makedirs(rawdir, exist_ok=True)
            with open(f"{rawdir}/{self.id}.json", 'w') as fp:
                json.dump(illust, fp, ensure_ascii=False)
        self.createdTime = int(time.time())
        if size == IllustSize.MEDIUM:
            url = illust["image_urls"]["medium"]
        elif size == IllustSize.LARGE:
            url = illust["image_urls"]["large"]
        elif size == IllustSize.ORIGINAL:
            if illust["page_count"] == 1:
                url = illust["meta_single_page"]["original_image_url"]
            else:
                url = illust["meta_pages"][0]["image_urls"]["original"]
        else:
            raise ValueError(f"Unsupport illust size")

        self.title = illust["title"]
        self.size = (illust["width"], illust["height"])
        if mode:
            self.fp = BytesIO()
            self.agent.download(url, fname=self.fp)
            self.filesize = len(self.fp.getvalue())
        else:
            self.fp = url.replace("i.pximg.net", "i.pixiv.cat")
            self.filesize = 0
        self.authTags = [x["name"] for x in illust["tags"]]
        # TODO: user tag
        self.userTags = []
        self.rating = Rating.EXPLICIT if illust["x_restrict"] == 1 else Rating.UNKNOWN
        if illust["type"] == "illust":
            self.type = IllustType.ILLUST
        elif illust["type"] == "ugoira":
            self.type = IllustType.UGOIRA
        else:
            self.type = IllustType.UNKNOWN
            
    def __repr__(self) -> str:
        # return f"illust id:\t{self.id}\nfile size:\t{self.filesize/10e6:.2f}\ntags:\t\t{','.join(self.authTags)}\nrating:\t{self.rating.name}"
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "size": ','.join(str(x) for x in self.size),
            "filesize": self.filesize,
            "authTags": ','.join(self.authTags),
            "userTags": ','.join(self.userTags),
            "rating": self.rating.name,
            "type": self.type.name,
            "createdTime": self.createdTime
        }, ensure_ascii=False, indent=4)

    def toDict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "img": base64.b64encode(self.fp.getvalue()).decode() if isinstance(self.fp, BytesIO) else self.fp,
            "filesize": self.filesize,
            "authTags": ','.join(self.authTags),
            "userTags": ','.join(self.userTags),
            "rating": self.rating.name,
            "type": self.type.name,
            "title": self.title,
            "size": ','.join(str(x) for x in self.size),
            "createdTime": self.createdTime
        }