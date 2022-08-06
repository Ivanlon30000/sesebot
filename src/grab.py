from typing import *
from utils.const import TOKEN, CONFIG
from pixiv.grab import PixivRecommendedGrab, TagsFilter, PixivFollowGrab
from pixiv import get_agent
from pixivpy3 import PixivError
from utils.basic_config import get_logger, get_database
import schedule
import time

logger = get_logger("grab2")
db, _ = get_database()
logger.info("Pixiv logining ...")
try:
    PAPI = get_agent()
except PixivError:
    logger.error("Pixiv login failed")
    exit(101)


recommendedGrab = PixivRecommendedGrab(db=db, papi=PAPI, num=CONFIG["recommend_num"],
                                       expire=CONFIG["expire"], filters=[TagsFilter(noTags=["R-18"])])

followGrab = PixivFollowGrab(db=db, papi=PAPI)


schedule.every(CONFIG["interval"]).seconds.do(recommendedGrab.grab)
schedule.every(10).minutes.do(followGrab.grab)

logger.info(f"{len(schedule.get_jobs())} grab schedule running")
while True:
    schedule.run_pending()
    time.sleep(10)
