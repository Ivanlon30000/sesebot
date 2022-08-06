import datetime
import re
import time
from typing import *

import telebot
from telebot.types import *
from telebot.types import InputMediaPhoto
from telebot.util import quick_markup

from bot import bot_send_illust, remove_reply_markup_item
from pixiv import illust_bookmark_add, illust_image_urls
from utils.basic_config import get_database, get_logger
from utils.const import CONFIG, TOKEN
from utils.feed import random_feed_interactive

logger = get_logger("bot")

logger.info("Connecting Redis db: {}:{}".format(
    CONFIG["db_host"], CONFIG["db_port"]))
db, _ = get_database()
logger.info("Redis db connected")

bot = telebot.TeleBot(TOKEN["bot"])

@bot.message_handler(commands=["start", "help"])
def start(message: Message):
    bot.reply_to(message, "说，你想涩涩")
    

@bot.message_handler(regexp=r"(se|色|涩){2}|(se|色|涩)(图|tu)|不够[涩色]")
def sese(message: Message):
    logger.debug(f"Receive msg: {message}")
    chat_id = message.chat.id
    feed = random_feed_interactive(db, chat_id)
    if feed.__next__():
        bot.reply_to(message, "涩图来力！")
        illust = feed.__next__()
        bot_send_illust(bot, chat_id, illust)
    else:
        logger.info("No image available.")
        bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
        bot.send_message(message.chat.id, "还要涩涩？还要涩涩？还要涩涩？")


@bot.callback_query_handler(func=lambda x: re.match(r"like:\w+:\d+", x.data))
def echo_query(query: CallbackQuery):
    parts = query.data.split(':')
    if len(parts) == 3:
        _, group, illustId = parts
    else:
        _, illustId = parts
        group = "illust"
        
    logger.info(f"Bookmark query pix:{illustId}")
    try:
        illust = db.hgetall(f"{group}:{illustId}")
        res = illust_bookmark_add(illust)
    except:
        logger.error(f"Bookmark {illustId} error")
        bot.answer_callback_query(query.id, f"{illustId} 收藏出错")
    else:
        logger.info(f"Bookmark {illustId} done")
        
        bot.answer_callback_query(query.id)
        bot.reply_to(query.message, f"{illustId} 已收藏")
        remove_reply_markup_item(bot, query.message, "收藏")
        logger.info(f"Reply markup modified")
    

@bot.callback_query_handler(func=lambda x: re.match(r"seeall:\d+", x.data))
def seeall(query: CallbackQuery):
    logger.debug(f"seeall query: {query}")
    _, iid = query.data.split(":")
    urls = illust_image_urls(iid)
    if urls is not None:
        logger.info(f"Sending {iid} all images")
        media = [InputMediaPhoto(url) for url in urls]
        bot.send_media_group(query.message.chat.id, media, reply_to_message_id=query.message.id)
        logger.info(f"{len(urls)} images sent")
        remove_reply_markup_item(bot, query.message, "全部")
        logger.info(f"Reply markup modified")
    else:
        bot.send_message(query.message.chat.id, f"出错力！")
        
@bot.message_handler(commands=["/ping"])
def echo_chatid(message: Message):
    bot.send_message(message.chat.id, message.chat.id)

@bot.message_handler(func=lambda x: True)
def echo(message: Message):
    time = datetime.datetime.now()
    if time.minute == 0:
        text = f"{time.hour}点整"
    else:
        text = f"{time.hour}点{time.minute}分"
    text = f"布谷——布谷——。幽夜净土时间{text}。"
    bot.send_message(message.chat.id, text)

def main():
    logger.info("Bot looping")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__": 
    main()
