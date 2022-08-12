from typing import *

from . import bot, logger

import re
from telebot.types import Message, CallbackQuery
import utils.db
from telebot.util import quick_markup

    
@bot.message_handler(func=lambda x: re.match(r"/level ?(.*)$", x.text))
def set_sanity_level_message(message: Message):
    logger.info(f"Set sanity level {message.text}")
    level = utils.db.get_sanity_level(message.chat.id)
    if not level:
        level = "未设置"
    
    mat = re.match(r"/level ?(\d(,\d)*|\d?-\d?)$", message.text)
    if mat:
        expr = mat.group(1)
        # newLevel = set_sanity_level(db, message.chat.id, expr)
        newLevel = utils.db.set_sanity_level(message.chat.id, expr)
        logger.info(f"Old level: {level}, new level: {newLevel}")
        
        if newLevel:
            text = f"过滤器已设为 {newLevel}"
        else:
            text = "过滤器表达式错误，支持的表达式：\n1. ','分割: 2,4,6\n2. '-'分割: 2-6"
        markup = None
    else:
        text = f"当前过滤等级：{level}\n设置新的过滤等级：\n(只推送小于或等于指定等级以下的涩图)"
        markup = quick_markup({
            "≦2": {"callback_data": "setlevel:0-2"},
            "≦4": {"callback_data": "setlevel:0-4"},
            "≦6": {"callback_data": "setlevel:0-6"}}, row_width=3)
        
    bot.send_message(message.chat.id, text, 
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda x:re.match(r"setlevel:\d+", x.data))
def set_sanity_level_query(query: CallbackQuery):
    sanityLevel = query.data.split(":")[-1]
    logger.info(f"Sanity level query received: {query.data}")
    # newLevel = set_sanity_level(db, query.message.chat.id, sanityLevel)
    newLevel = utils.db.set_sanity_level(query.message.chat.id, sanityLevel)
    if newLevel:
        bot.reply_to(query.message, f"过滤等级已设为 {newLevel}")
        logger.info(f"Sanity level set to {newLevel}")
    else:
        logger.inf(f"Failed to set sanity level to {sanityLevel}")
    bot.answer_callback_query(query.id)


@bot.message_handler(commands=["quota"])
def echo_quota(message: Message):
    quota = utils.db.query_all_illusts_id(message.chat.id, "illust", applySanity=True)
    bot.send_message(message.chat.id, f"宁有 {len(quota)} 张涩图库存")    