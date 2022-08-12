import datetime
from typing import *

from telebot.types import Message

from . import bot, logger


@bot.message_handler(func=lambda x: True)
def echo(message: Message):
    time = datetime.datetime.now()
    if time.minute == 0:
        text = f"{time.hour}点整"
    else:
        text = f"{time.hour}点{time.minute}分"
    text = f"布谷——布谷——。幽夜净土时间{text}。"
    bot.send_message(message.chat.id, text)
