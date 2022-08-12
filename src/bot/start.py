from typing import *

import telebot
from telebot.types import *

from . import bot


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
    
    
@bot.message_handler(commands=["ping"])
def echo_chatid(message: Message):
    bot.send_message(message.chat.id, message.chat.id)
    