import random
from typing import *
import re

from pixiv import PixivIllust
from redis import Redis

from utils.basic_config import get_logger

logger = get_logger(__name__)

def query_all_illusts_id(db:Redis, chatid:int, group:str, applySanity:bool) -> List[str]:
    imglist = [x.split(':')[-1] for x in db.keys(f"{group}:*")]
    userSeen = db.smembers(f"user_seen:{chatid}")
    userLevel = db.hget("sanityLevel", chatid)
    if userLevel:
        userLevel = userLevel.split(',')
    else:
        userLevel = ['2', '4', '6']
    logger.info(f"user {chatid} level: {userLevel}")
    result = []
    for illustId in imglist:
        if illustId in userSeen:
            continue
        
        if applySanity:
            illustLevel = db.hget(f"{group}:{illustId}", "sanityLevel")
            # logger.debug(f"Illust {illustId} sanity level: {illustLevel}")
            if not illustLevel:
                continue
            if illustLevel not in userLevel:
                continue
        
        result.append(illustId)
    return result


def feed_all_interactive(db:Redis, chatid:int, group:str, applySanity:bool=False) -> Generator[PixivIllust | int, None, None]:
    imglist = query_all_illusts_id(db, chatid, group, applySanity=applySanity)
    yield len(imglist)
    if len(imglist) > 0:
        for illustId in imglist:
            illust = db.hgetall(f"{group}:{illustId}")
            logger.debug(illust)
            illust = PixivIllust(dbDict=illust)
            db.sadd(f"user_seen:{chatid}", illustId)
            yield illust

   
def feed_all(db:Redis, chatid:int, group:str, applySanity:bool=False) -> Generator[PixivIllust, None, None]:
    feed = feed_all_interactive(db, chatid, group, applySanity=applySanity)
    if feed.__next__():
        for illust in feed:
            yield illust
    else:
        raise StopIteration()
    

def random_feed_interactive(db:Redis, chatid:int, group:str="illust", applySanity:bool=True) -> Generator[PixivIllust | bool, None, None]:
    imglist = query_all_illusts_id(db, chatid, group, applySanity=applySanity)
    if len(imglist) > 0:
        yield True
        illustId = random.choice(imglist)
        logger.info("Image {} selected".format(illustId))
        illust = db.hgetall(f"{group}:{illustId}")
        logger.debug(illust)
        illust = PixivIllust(dbDict=illust)
        db.sadd(f"user_seen:{chatid}", illustId)
        yield illust
    else:
        yield False


def random_feed(db:Redis, chatid:int, group:str="illust", applySanity:bool=True) -> Optional[PixivIllust]:
    feed = random_feed_interactive(db, chatid, group, applySanity=applySanity)
    res = feed.__next__()
    if res:
        return feed.__next__()
    else:
        return None


def set_sanity_level(db:Redis, chatid:int, sanityLevel:str|List[str|int]) -> str:
    if isinstance(sanityLevel, list):
        newLevel = (str(x) for x in sanityLevel)
    elif isinstance(sanityLevel, str):
        mat = re.match(r"(\d(,\d)*|\d?-\d?)$", sanityLevel)
        if mat:
            expr = mat.group(1)
            if '-' in expr:
                s, e = expr.split('-')
                s = int(s) if s else 2
                e = int(e) if e else 6
                newLevel = (str(x) for x in range(s, e+1, 2))
            else:
                newLevel = expr.split(',')
        else:
            newLevel = [] 
    elif isinstance(sanityLevel, int):
        newLevel = {str(sanityLevel)}
    else:
        raise ValueError(f"Param 'sanityLevel' type error")
    newLevel = ','.join(x for x in set(x for x in newLevel if x in {'2', '4', '6'}))
    if newLevel:
        db.hset("sanityLevel", chatid, newLevel)
    return newLevel