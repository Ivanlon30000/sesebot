import re
from typing import *

from telebot.types import CallbackQuery

import utils.db
import utils.pixiv

from . import bot, logger
from .util import remove_message_reply_markup_item


@bot.callback_query_handler(func=lambda x: re.match(r"like:\w+:\d+", x.data))
def echo_query(query: CallbackQuery):
    parts = query.data.split(':')
    if len(parts) == 3:
        _, group, illustId = parts
    else:
        _, illustId = parts
        group = "illust"
        
    logger.info(f"Bookmark query pix:{illustId}")
    # illust = db.hgetall(f"{group}:{illustId}")
    # utils.db.get_illust(group, illustId)
    
    # res = illust_bookmark_add(illust)
    res = utils.pixiv.add_bookmark(illustId)
    if res is None:
        logger.error(f"Bookmark {illustId} error")
        bot.answer_callback_query(query.id, f"{illustId} 收藏出错")
    else:
        logger.info(f"Bookmark {illustId} done")
        
        bot.answer_callback_query(query.id)
        bot.reply_to(query.message, f"{illustId} 已收藏")
        remove_message_reply_markup_item(bot, query.message, "收藏")
        logger.info(f"Reply markup modified")
    