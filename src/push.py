from collections import UserDict
from time import sleep
from typing import *

import schedule

from bot.util import send_illust
from utils.db import random_feed
from utils.log import get_logger, with_log

logger = get_logger(__name__)
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
        
    def start(self) -> schedule.Job:
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

from utils.const import ME

job = RandomFeedJob(30, ME, region="*", applySanity=True)
# job.start()

job.run()
# while True:
#     schedule.run_pending()
#     sleep(1)
