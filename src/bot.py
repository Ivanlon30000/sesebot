import datetime
import re
from typing import *

import telebot
from telebot.types import *
from telebot.util import quick_markup

from pixiv import illust_bookmark_add
from utils.basic_config import get_database, get_logger
from utils.const import CONFIG, TOKEN
from utils.feed import random_feed_interactive, to_photo

logger = get_logger("bot")

logger.info("Connecting Redis db: {}:{}".format(
    CONFIG["db_host"], CONFIG["db_port"]))
db, _ = get_database()
logger.info("Redis db connected")

whitelist = TOKEN["whitelist"]
bot = telebot.TeleBot(TOKEN["bot"])

@bot.message_handler(commands=["start", "help"])
def start(message: Message):
    bot.reply_to(message, "说，你想涩涩")
    

@bot.message_handler(regexp=r"(se|色|涩){2}|(se|色|涩)(图|tu)|不够涩")
def sese(message: Message):
    logger.debug(f"Receive msg: {message}")
    chat_id = message.chat.id
    feed = random_feed_interactive(db, chat_id)
    if feed.__next__():
        bot.reply_to(message, "涩图来力！")
        illust = feed.__next__()
        photo = to_photo(illust["img"])
        caption = '\n'.join([
            illust["title"],
            "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
            "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
        ])
        
        if chat_id in whitelist:
            markup = quick_markup({
                'bookmark!': {'callback_data': 'like:'+illust["id"]}
            })
        else:
            markup = None
        bot.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=markup)
        logger.info("Image sent")
    else:
        logger.info("No image available.")
        bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
        bot.send_message(message.chat.id, "还要涩涩？还要涩涩？还要涩涩？")

@bot.callback_query_handler(func=lambda x: re.match(r"like:\d+", x.data))
def echo_query(query: CallbackQuery):
    illustId = query.data.split(':')[-1]
    logger.info(f"Bookmark query pix:{illustId}")
    illust = db.hgetall(f"illust:{illustId}")
    res = illust_bookmark_add(illust)
    if res is not None:
        bot.reply_to(query.message, f"{illustId}已收藏")
    else:
        bot.reply_to(query.message, f"{illustId}收藏出错")

@bot.message_handler(func=lambda x: True)
def echo(message: Message):
    time = datetime.datetime.now()
    if time.minute == 0:
        text = f"{time.hour}点整"
    else:
        text = f"{time.hour}点{time.minute}分"
    text = f"布谷——布谷——。幽夜净土时间{text}。"
    bot.send_message(message.chat.id, text)


if __name__ == "__main__": 
    logger.info("Bot looping")
    bot.infinity_polling(skip_pending=True)
