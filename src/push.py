from abc import ABC, abstractmethod
from time import sleep
from typing import *

import schedule

from bot.util import send_illust, send_message
from utils.const import CONFIG, TOKEN
from utils.db import random_feed
from utils.log import get_logger, with_log
from utils.types import Dumpable

logger = get_logger(__name__ if __name__ != "__main__" else "push")
logd = with_log(logger)

sc = schedule.Scheduler()

# interfaces


class FeedJobBase(ABC):
    def __init__(self, chatId: int, region: str = '*', introMsg: str | None = None) -> None:
        super().__init__()
        self.chatId = chatId
        self.region = region
        self.intro = introMsg
        self._job = None

    @property
    def job(self) -> schedule.Job:
        if self._job is None:
            raise ValueError("Call `register_job` first")
        return self._job

    @job.setter
    def job(self, __val) -> None:
        self._job = __val

    def run(self) -> None:
        if self.intro is not None:
            send_message(chat_id=self.chatId, text=self.intro)
        self.feed()

    @abstractmethod
    def feed(self) -> None:
        pass

    @abstractmethod
    def register_job(self) -> schedule.Job:
        pass

    def cancel(self):
        schedule.cancel_job(self.job)


class RandomFeedJobBase(FeedJobBase):
    def feed(self) -> None:
        logger.info(f"Random feed  for {self.chatId}")
        illust = random_feed(self.chatId, self.region)
        if illust is None:
            logger.warning(
                f"No available illust for {self.chatId}, push failed")
        else:
            logger.info(f"Sending {illust} to {self.chatId}")
            send_illust(self.chatId, illust)
        logger.info(f"Random feed done.")


class PeriodicalFeedJobBase(FeedJobBase):
    def register_job(self, interval: int | None = None) -> schedule.Job:
        if interval is not None:
            self.interval = interval
        elif self.interval is not None:
            pass
        else:
            raise ValueError(f"interval is required")
        self.job = sc.every(self.interval).seconds.do(self.run)
        return self.job


class TimedFeedJobBase(FeedJobBase):
    def register_job(self, datetime: str | None = None) -> schedule.Job:
        if datetime is not None:
            self.datetime = datetime
        elif self.datetime is not None:
            pass
        else:
            raise ValueError(f"datetime is required")
        self.job = sc.every().day.at(self.datetime).do(self.run)
        return self.job

# feed classes


class PeroidicFeedJob(RandomFeedJobBase, PeriodicalFeedJobBase, Dumpable):
    @overload
    def _INT_ATTR(cls) -> Iterable[str]:
        return {"interval", "chatId"}

    @overload
    def _STRING_ATTR(cls) -> Iterable[str]:
        return {"region"}


class TimedFeedJob(RandomFeedJobBase, TimedFeedJobBase, Dumpable):
    @overload
    def _INT_ATTR(cls) -> Iterable[str]:
        return {"chatId"}

    @overload
    def _STRING_ATTR(cls) -> Iterable[str]:
        return {"region", "datetime"}


class ImmediatePushJob:
    def __init__(self) -> None:
        raise NotImplementedError()


jobs = [
    *(PeroidicFeedJob(chatid).register_job(CONFIG["push"]["interval"]) for chatid in CONFIG["push"]["list"]),
]

def main():
    logger.info(f"Start push loop")
    logger.info(f"{len(jobs)} jobs registered")
    
    while True:
        sc.run_pending()
        sleep(1)


if __name__ == "__main__":
    main()
