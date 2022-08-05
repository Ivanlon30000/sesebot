from typing import *
import schedule
import time
from utils.feed import random_feed, to_photo
from utils.basic_config import get_database, get_logger
import telebot
from telebot.util import quick_markup
import json
from utils.const import TOKEN

logger = get_logger("push")
bot = telebot.TeleBot(TOKEN["bot"])
db, _ = get_database()
whitelist = TOKEN["whitelist"]


def daily_push(text:str):
    chats = [x.split(':')[-1] for x in db.keys("user_seen:*")]
    for chatId in chats:
        if len(whitelist) == 0 or chatId in whitelist:
            illust = random_feed(db, chatId)
            if illust is not None:
                logger.info(f"Push {illust['id']} to {chatId}, text: {text}")
                bot.send_message(chatId, text)
                if chatId == str(TOKEN["chatid_me"]):
                    markup = quick_markup({
                        'bookmark!': {'callback_data': 'like:'+illust["id"]}
                    })
                else:
                    markup = None
                bot.send_photo(chatId, to_photo(illust["img"]), caption='\n'.join([
                    illust["title"],
                    "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
                    "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
                ]), reply_markup=markup)
            else:
                pass


schedule.every().day.at("08:00").do(daily_push, text="起床辣！这是派蒙给你的早安涩图~")
schedule.every().day.at("12:30").do(daily_push, text="中午辣！这是派蒙给你的午安涩图~")
schedule.every().day.at("22:30").do(daily_push, text="晚上辣！这是派蒙给你的晚安涩图~")
logger.info(f"{len(schedule.get_jobs())} schedule running")

while True:
    schedule.run_pending()
    time.sleep(10)