from io import BytesIO
from typing import *
import random
from utils.basic_config import get_logger
import base64

logger = get_logger(__name__)

def random_feed_interactive(db, chatid:int):
    imglist = [x.split(':')[-1] for x in db.keys("illust:*")]
    logger.debug(f"Image list: {imglist}")
    user_seen = db.smembers(f"user_seen:{chatid}")
    imglist = [x for x in imglist if x not in user_seen]
    logger.info("{} images available for {}".format(len(imglist), chatid))
    if len(imglist) > 0:
        yield True
        illustId = random.choice(imglist)
        logger.info("Image {} selected".format(illustId))
        illust = db.hgetall(f"illust:{illustId}")
        # if illust["img"].startswith("http"):
        #     photo = illust["img"]
        # else:
        #     photo = BytesIO(base64.b64decode(illust["img"]))
        # yield photo
        db.sadd(f"user_seen:{chatid}", illustId)
        yield illust
    else:
        yield None

def random_feed(db, chatid:int) -> Optional[Dict[str, Any]]:
    feed = random_feed_interactive(db, chatid)
    res = feed.__next__()
    if res:
        return feed.__next__()
    else:
        return None
    
def to_photo(img:str):
    return img if img.startswith("http") else BytesIO(base64.b64decode(img))
