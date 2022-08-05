from typing import *
from utils.const import TOKEN, CONFIG
from pixiv.grab import PixivRecommendedGrab, TagsFilter, UniqueFilter
from pixiv import get_agent
from pixivpy3 import PixivError
from utils.basic_config import get_logger, get_database

logger = get_logger("grab2")
db, _ = get_database()
logger.info("Pixiv logining ...")
try:
    PAPI = get_agent()
except PixivError:
    logger.error("Pixiv login failed")
    exit(101)

uniqueFilter = UniqueFilter(db)
r18Filter = TagsFilter(noTags=["R-18"])

grab = PixivRecommendedGrab(db=db, papi=PAPI, num=CONFIG["recommend_num"], 
                            expire=CONFIG["expire"], interval=CONFIG["interval"],
                            errInterval=CONFIG["error_interval"], filters=[uniqueFilter, r18Filter])

grab.run()