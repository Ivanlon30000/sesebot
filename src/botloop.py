import datetime
import re
from typing import *

import telebot
from telebot.types import *
from telebot.util import quick_markup

from bot import bot_send_illust, remove_reply_markup_item
from pixiv import illust_bookmark_add, illust_image_urls
from utils.basic_config import get_database, get_logger
from utils.const import CONFIG, TOKEN
from utils.feed import random_feed_interactive, query_all_illusts_id, set_sanity_level

logger = get_logger("bot")

logger.info("Connecting Redis db: {}:{}".format(
    CONFIG["db_host"], CONFIG["db_port"]))
db, _ = get_database()
logger.info("Redis db connected")

bot = telebot.TeleBot(TOKEN["bot"])


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id, "说，你想涩涩")


@bot.message_handler(commands=["help"])
def echo_help(message: Message):
    text = """/start - 开始
/help - 帮助
/ping - 返回你的chat id
/level - 设置过滤等级, e.g. "/level 2-4" or "/level 4,6"
/quota - 查看涩图库存"""
    bot.send_message(message.chat.id, text)


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
    illust = db.hgetall(f"{group}:{illustId}")
    res = illust_bookmark_add(illust)
    if res is None:
        logger.error(f"Bookmark {illustId} error")
        bot.answer_callback_query(query.id, f"{illustId} 收藏出错")
    else:
        logger.info(f"Bookmark {illustId} done")
        
        bot.answer_callback_query(query.id)
        bot.reply_to(query.message, f"{illustId} 已收藏")
        remove_reply_markup_item(bot, query.message, "收藏")
        logger.info(f"Reply markup modified")
    

@bot.callback_query_handler(func=lambda x: re.match(r"seeall:\d+", x.data))
def seeall_query(query: CallbackQuery):
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
    bot.answer_callback_query(query.id)
        
        
@bot.message_handler(commands=["ping"])
def echo_chatid(message: Message):
    bot.send_message(message.chat.id, message.chat.id)
    
    
@bot.message_handler(func=lambda x: re.match(r"/level ?(.*)$", x.text))
def set_sanity_level_message(message: Message):
    logger.info(f"Sanity level message received: {message.text}")
    level = db.hget("sanityLevel", message.chat.id)
    if not level:
        level = "未设置"
    
    mat = re.match(r"/level ?(\d(,\d)*|\d?-\d?)$", message.text)
    if mat:
        expr = mat.group(1)
        newLevel = set_sanity_level(db, message.chat.id, expr)
        logger.info(f"Old level: {level}, new level: {newLevel}")
        
        if newLevel:
            text = f"过滤器已设为 {newLevel}"
        else:
            text = "过滤器表达式错误，支持的表达式：\n1. ','分割: 2,4,6\n2. '-'分割: 2-6"
        markup = None
    else:
        text = f"当前过滤等级：{level}\n设置新的过滤等级：\n(只推送小于或等于指定等级以下的涩图)"
        markup = quick_markup({
            "2": {"callback_data": "setlevel:2"},
            "≦4": {"callback_data": "setlevel:4"},
            "≦6": {"callback_data": "setlevel:6"}}, row_width=3)
        
    bot.send_message(message.chat.id, text, 
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda x:re.match(r"setlevel:\d+", x.data))
def set_sanity_level_query(query: CallbackQuery):
    sanityLevel = query.data.split(":")[-1]
    logger.info(f"Sanity level query received: {query.data}")
    newLevel = set_sanity_level(db, query.message.chat.id, '-'+sanityLevel)
    if newLevel:
        bot.reply_to(query.message, f"过滤等级已设为 {newLevel}")
        logger.info(f"Sanity level set to {newLevel}")
    else:
        logger.inf(f"Failed to set sanity level to {sanityLevel}")
    bot.answer_callback_query(query.id)


@bot.message_handler(commands=["quota"])
def echo_quota(message: Message):
    quota = query_all_illusts_id(db, message.chat.id, "illust", applySanity=True)
    bot.send_message(message.chat.id, f"宁有 {len(quota)} 张涩图库存")    
    
    
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
