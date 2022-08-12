import time
from typing import *

import schedule
import telebot

from bot import send_illust
from utils.basic_config import get_database, get_logger
from utils.const import TOKEN, CONFIG
from utils.feed import feed_all_interactive, random_feed

logger = get_logger("push")
bot = telebot.TeleBot(TOKEN["bot"])
db, _ = get_database()
WHITELIST = TOKEN["whitelist"]
ME = TOKEN["chatid_me"]


def daily_push(text:str):
    chats = [x.split(':')[-1] for x in db.keys("user_seen:*")]
    for chatId in chats:
        if len(WHITELIST) == 0 or chatId in WHITELIST:
            illust = random_feed(db, chatId)
            if illust is not None:
                logger.info(f"Push {illust.id} to {chatId}, text: {text}")
                bot.send_message(chatId, text)
                send_illust(bot, chatId, illust)
            else:
                pass

schedule.every().day.at("08:00").do(daily_push, text="起床辣！这是派蒙给你的早安涩图~")
schedule.every().day.at("12:30").do(daily_push, text="中午辣！这是派蒙给你的午安涩图~")
schedule.every().day.at("22:30").do(daily_push, text="晚上辣！这是派蒙给你的晚安涩图~")


def follow_push():
    group="follow"
    logger.info("Start push follow")
    feed = feed_all_interactive(db, ME, group=group)
    num = feed.__next__()
    logger.info(f"{num} new follow")
    if num > 0:
        bot.send_message(ME, f"有{num}张新的涩图辣！")
        for illust in feed:
            logger.info(f"Push follow illust: {illust}")
            send_illust(bot, ME, illust, group=group)

push_job = schedule.every(CONFIG["follow_check_interval"]).minutes.do(follow_push)

def main():
    logger.info(f"{len(schedule.get_jobs())} schedule running")
    push_job.run()
    while True:
        schedule.run_pending()
        time.sleep(10)
        
if __name__ == "__main__":
    main()
