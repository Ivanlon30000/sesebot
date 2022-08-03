from typing import *
import schedule
import time
from utils.feed import random_feed, to_photo
from utils import get_database, get_logger
import telebot
import json

logger = get_logger(__name__)

with open("token.json") as fp:
    _token = json.load(fp)
bot = telebot.TeleBot(_token["bot"])

db, _ = get_database()

whiteList = []

def push(text:str):
    chats = [x.split(':')[-1] for x in db.keys("user_seen:*")]
    for chatId in chats:
        if len(whiteList) == 0 or chatId in whiteList:
            illust = random_feed(db, chatId)
            if illust is not None:
                logger.info(f"Push {illust['id']} to {chatId}, text: {text}")
                bot.send_message(chatId, text)
                bot.send_photo(chatId, to_photo(illust["img"]), caption='\n'.join([
                    illust["title"],
                    "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
                    "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
                ]))
            else:
                pass

schedule.every().day.at("08:00").do(push, text="起床辣！这是派蒙给你的早安涩图~")
schedule.every().day.at("12:30").do(push, text="中午辣！这是派蒙给你的午安涩图~")
schedule.every().day.at("22:30").do(push, text="晚上辣！这是派蒙给你的晚安涩图~")
logger.info(f"{len(schedule.get_jobs())} schedule running")

while True:
    schedule.run_pending()
    time.sleep(10)