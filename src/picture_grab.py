import time
from typing import *

from pixivpy3.utils import PixivError

from utils.basic_config import get_config, get_database, get_logger
from pixiv import get_agent, PixivIllust


CONFIG = get_config()

logger = get_logger("grab")

REDIS_HOST = CONFIG["db_host"]
REDIS_PORT = CONFIG["db_port"]
logger.info(f"Connecting redis {REDIS_HOST}:{REDIS_PORT}")
db, dbinfo = get_database()
logger.info("Redis db connected.")
    

logger.info("Pixiv logining ...")
try:
    PAPI = get_agent()
except PixivError:
    logger.error("Pixiv login failed")
    exit(101)

# function
def grab(num:int, expire:int) -> List[int]:
    result = []
    logger.info("Start grab")
    logger.info("Getting pixiv recommended ...")
    try:
        recommended = PAPI.illust_recommended()
        recommended = recommended["illusts"][:num]
    except (PixivError, KeyError):
        logger.warning("Pixiv Error, skip")
        return None

    # existIllust = [int(x) for x in db.smembers("illusts")]
    existIllust = set(db.keys("illust:*"))
    logger.info("Got {} recommended illusts".format(len(recommended)))
    for illust in recommended:
        # logger.info("Got illust {}".format(illust["id"]))
        if f'illust:{illust["id"]}' in existIllust:
            logger.info("Illust {} already exists, skip.".format(illust["id"]))
        else:
            try:
                illustObj = PixivIllust(PAPI, illust=illust, rawdir=CONFIG["json_raw_savedir"])
            except PixivError:
                logger.warning(
                    "Download {}: Pixiv Error, skip.".format(illust["id"]))
                continue
            if "R-18" in illustObj.authTags:
                continue
            logger.info("Illust {} added.".format(illust["id"]))
            # db.sadd("illusts", illust["id"])
            key = "illust:{}".format(illust["id"])
            db.hset(key, mapping=illustObj.toDict())
            db.expire(key, expire)
            result.append(illust["id"])
    logger.info("Grab done, {} added: {}".format(
        len(result), ','.join(str(x) for x in result)))
    return result
    

def run():
    interval = CONFIG["interval"]
    errInterval = CONFIG["error_interval"]
    num = CONFIG["recommend_num"]
    expire = CONFIG["expire"]
    
    while True:
        result = grab(num, expire)
        if result is None:
            logger.info(f"Sleep for {errInterval}s")
            time.sleep(errInterval)
        else:
            logger.info(f"Sleep for {interval}s")
            time.sleep(interval)

if __name__ == "__main__":
    run()
