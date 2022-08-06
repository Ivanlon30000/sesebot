import base64
import random
from io import BytesIO
from typing import *

from redis import Redis

from utils.basic_config import get_logger
from pixiv import PixivIllust

logger = get_logger(__name__)

def query_all_illusts_id(db:Redis, chatid:int, group:str) -> List[str]:
    imglist = [x.split(':')[-1] for x in db.keys(f"{group}:*")]
    logger.debug(f"Image list: {imglist}")
    user_seen = db.smembers(f"user_seen:{chatid}")
    imglist = [x for x in imglist if x not in user_seen]
    logger.info("{} images available for {}".format(len(imglist), chatid))
    return imglist


def feed_all_interactive(db:Redis, chatid:int, group:str) -> Generator[PixivIllust | int, None, None]:
    imglist = query_all_illusts_id(db, chatid, group)
    yield len(imglist)
    if len(imglist) > 0:
        for illustId in imglist:
            illust = db.hgetall(f"{group}:{illustId}")
            logger.debug(illust)
            illust = PixivIllust(dbDict=illust)
            db.sadd(f"user_seen:{chatid}", illustId)
            yield illust

   
def feed_all(db:Redis, chatid:int, group:str) -> Generator[PixivIllust, None, None]:
    feed = feed_all_interactive(db, chatid, group)
    if feed.__next__():
        for illust in feed:
            yield illust
    else:
        raise StopIteration()
    

def random_feed_interactive(db:Redis, chatid:int, group:str="illust") -> Generator[PixivIllust | bool, None, None]:
    imglist = query_all_illusts_id(db, chatid, group)
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


def random_feed(db, chatid:int, group:str="illust") -> Optional[PixivIllust]:
    feed = random_feed_interactive(db, chatid, group)
    res = feed.__next__()
    if res:
        return feed.__next__()
    else:
        return None
