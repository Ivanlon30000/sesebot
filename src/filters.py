from typing import *
from utils.types import Illust
from utils.db import query_all_illusts_key

class FilterBase:
    def condition(self, illust:Illust) -> bool:
        return True

    def filter(self, illusts:List[Illust], **kwargs) -> List[Illust]:
        return [illust for illust in illusts if self.condition(illust)]

    def __call__(self, illusts:List[Illust], **kwargs) -> List[Illust]:
        return self.filter(illusts, **kwargs)

class AllpassFilter(FilterBase):
    pass

class UniqueFilter(FilterBase):
    def __init__(self, chatId:int|None=None) -> None:
        super().__init__()
        self.chatId = chatId
        
    def filter(self, illusts: List[Illust], **kwargs) -> List[Illust]:
        existIllust = set(query_all_illusts_key(self.chatId, region="*", applySanity=False))
        return [illust for illust in illusts if f"{illust.region}:{illust.id}" not in existIllust]

class TagsFilter(FilterBase):
    def __init__(self, hasTags:Iterable[str]=[], noTags:Iterable[str]=[]) -> None:
        super().__init__()
        self.whitelist = hasTags
        self.blacklist = noTags
        
    def condition(self, illust: Illust) -> bool:
        tags = set(illust.authTags+illust.userTags)
        if len(self.blacklist) == 0 or all(x not in tags for x in self.blacklist):
            return self.whitelist == 0 or all(x in tags for x in self.whitelist)
        else:
            return False
    
_defaultFilters = [AllpassFilter()]