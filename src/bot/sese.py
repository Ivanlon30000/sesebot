from typing import *

from telebot.types import Message
from utils import db

from . import bot, logger
from .util import send_illust


@bot.message_handler(regexp=r"(se|色|涩){2}|(se|色|涩)(图|tu)|不够[涩色]")
def sese(message: Message):
    logger.info(f"Receive sese message from {message.chat.id}")
    feed = db.random_feed_interactive(message.chat.id)
    if feed.__next__():
        bot.reply_to(message, "涩图来力！")
        logger.info(f"Reply sent")
        illust = feed.__next__()
        logger.info(f"Feed {illust}")
        send_illust(message.chat.id, illust)
        logger.info(f"setu sent")
    else:
        logger.info("No image available")
        bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
        bot.send_message(message.chat.id, "还要涩涩？还要涩涩？还要涩涩？")
        logger.info("Reply sent")

