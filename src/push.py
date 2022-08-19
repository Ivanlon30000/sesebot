from collections import UserDict
from time import sleep
from typing import *

import schedule

from bot.util import send_illust
from utils.const import ME
from utils.db import random_feed
from utils.log import get_logger, with_log

logger = get_logger(__name__ if __name__ != "__main__" else "push")
logd = with_log(logger)


class RandomFeedJob(UserDict):
    def __init__(self, interval:int, chatId:int, region:str, applySanity:bool) -> None:
        super().__init__()
        kwargs = {
            "chatId": chatId,
            "interval": interval,
            "region": region,
            "applySanity": applySanity
        }
        self.update(kwargs)
        self.job = None
    
    def run(self) -> None:
        logger.info(f"Random feed  for {self.chatId}")
        illust = random_feed(self.chatId, self.region, self.applySanity)
        if illust is None:
            logger.warning(f"No available illust for {self.chatId}, push failed")
        else:
            logger.info(f"Sending {illust} to {self.chatId}")
            send_illust(self.chatId, illust)
        logger.info(f"Random feed done.")
        
    def register(self) -> schedule.Job:
        self.job = schedule.every(self.interval).seconds.do(self.run)
        return self.job

    def cancel(self):
        schedule.cancel_job(self.job)
    
    def update(self, kwargs):
        super().update(kwargs)
        for k, v in kwargs.items():
            self.__setattr__(k, v)
    
    @classmethod
    def from_db(cls, kwargs) -> "RandomFeedJob":
        return cls(**kwargs)


jobs = [
    RandomFeedJob(30, ME, region="*", applySanity=True),
]


def run():
    logger.info(f"Start push loop")
    logger.info(f"{len(jobs)} jobs to register")
    for job in jobs:
        job.register()
    logger.info(f"{len(jobs)} jobs registered")
    
    while True:
        schedule.run_pending()
        sleep(1)
        
if __name__ == "__main__":
    run()
