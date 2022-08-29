import re
from typing import *

import utils.db
from telebot.types import CallbackQuery, Message
from telebot.util import quick_markup

from . import bot, logger


@bot.message_handler(func=lambda x: re.match(r"/level ?(.*)$", x.text))
def set_sanity_level_message(message: Message):
    logger.info(f"Set sanity level message received from {message.chat.id}: {message.text=}")
    level = utils.db.get_sanity_level(message.chat.id)

    logger.info(f"Current level: {level=}")
    mat = re.match(r"/level ?(\d(,\d)*|\d?-\d?)$", message.text)
    if mat:
        expr = mat.group(1)
        newLevel = utils.db.set_sanity_level(message.chat.id, expr)
        logger.info(f"New level set: {newLevel=}")
        
        if newLevel:
            text = f"过滤器已设为 {newLevel}"
        else:
            text = "过滤器表达式错误，支持的表达式：\n1. ','分割: 2,4,6\n2. '-'分割: 2-6"
        markup = None
    else:
        text = f"当前过滤等级：{','.join(str(x) for x in level) if level else '未设置'}\n设置新的过滤等级：\n(只推送小于或等于指定等级以下的涩图)"
        markup = quick_markup({
            "≦2": {"callback_data": "setlevel:0-2"},
            "≦4": {"callback_data": "setlevel:0-4"},
            "≦6": {"callback_data": "setlevel:0-6"}}, row_width=3)
        
    bot.send_message(message.chat.id, text, 
                     reply_markup=markup)
    logger.info(f"Reply message sent")

@bot.callback_query_handler(func=lambda x:re.match(r"setlevel:\d+", x.data))
def set_sanity_level_query(query: CallbackQuery):
    logger.info(f"Sanity level query received from {query.message.chat.id}: {query.data=}")
    sanityLevel = query.data.split(":")[-1]
    newLevel = utils.db.set_sanity_level(query.message.chat.id, sanityLevel)
    if newLevel:
        bot.reply_to(query.message, f"过滤等级已设为 {newLevel}")
        logger.info(f"Sanity level set to {newLevel}")
    else:
        logger.inf(f"Failed to set sanity level to {sanityLevel}")
    bot.answer_callback_query(query.id)
    logger.info(f"Query answered")


@bot.message_handler(commands=["quota"])
def echo_quota(message: Message):
    logger.info(f"Quota command received from {message.chat.id}: {message.text=}")
    quota = utils.db.query_all_illusts_key(message.chat.id, "*", applySanity=True)
    bot.send_message(message.chat.id, f"宁有 {len(quota)} 张涩图库存")
    logger.info(f"Quota reply message sent")
