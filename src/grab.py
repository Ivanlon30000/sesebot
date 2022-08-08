import time
from typing import *

import schedule
from pixivpy3 import PixivError

from pixiv import get_agent, refresh_token
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
                                       expire=CONFIG["expire"], filters=[
                                           TagsFilter(noTags=["R-18", "3D", "3DCG"]),
                                           ])

followGrab = PixivFollowGrab(db=db, papi=PAPI, expire=CONFIG["expire"])

grabs = []
grabs.append(schedule.every(CONFIG["interval"]).seconds.do(recommendedGrab.grab))
grabs.append(schedule.every(CONFIG["follow_check_interval"]).minutes.do(followGrab.grab))
schedule.every().hour.do(refresh_token)


def main():
    logger.info(f"{len(schedule.get_jobs())} schedule running")
    [g.run() for g in grabs]
    while True:
        schedule.run_pending()
        time.sleep(10)
        
if __name__ == "__main__":
    main()
