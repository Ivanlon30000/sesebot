import time
from typing import *

import schedule
from pixivpy3 import PixivError

from pixiv import get_agent
from pixiv.grab import PixivFollowGrab, PixivRecommendedGrab, TagsFilter
from utils.basic_config import get_database, get_logger
from utils.const import CONFIG, TOKEN

logger = get_logger("grab")
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
schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(10)
