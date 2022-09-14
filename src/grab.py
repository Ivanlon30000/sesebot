from time import sleep

import schedule

from filters import TagsFilter
from grabbers.pixiv import PixivRecommendedGrab
from utils.const import CONFIG
from utils.log import get_logger

logger = get_logger("grab")

grabbers = [
    PixivRecommendedGrab(
        filters=[TagsFilter(noTags=["R-18", "3D", "3DCG"])], expire=CONFIG["expire"]),
]

sc = schedule.Scheduler()
jobs = [sc.every(CONFIG["grab"]["interval"]).seconds.do(grabber.grab) for grabber in grabbers]


def main():
    logger.info("Start grab looping")
    logger.info(f"{len(grabbers)} grab running")

    while True:
        sc.run_pending()
        sleep(1)
        
if __name__ == "__main__":
    main()
