from typing import *

from telebot.types import Message

from . import bot, logger


@bot.message_handler(commands=["start"])
def start(message: Message):
    logger.info(f"Start message received from {message.chat.id}")
    bot.send_message(message.chat.id, "说，你想涩涩")
    logger.info(f"Start message reply message sent")


@bot.message_handler(commands=["help"])
def echo_help(message: Message):
    logger.info(f"Help message received from {message.chat.id}")
    text = """/start - 开始
/help - 帮助
/ping - 返回你的chat id
/level - 设置过滤等级, e.g. "/level 2-4" or "/level 4,6"
/quota - 查看涩图库存"""
    bot.send_message(message.chat.id, text)
    logger.info(f"Help message reply message sent")
    
    
@bot.message_handler(commands=["ping"])
def echo_chatid(message: Message):
    logger.info(f"Ping message received from {message.chat.id}")
    bot.send_message(message.chat.id, message.chat.id)
    logger.info(f"Ping message reply message sent")
    