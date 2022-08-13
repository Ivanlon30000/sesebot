import pickle
import re
from typing import *

import utils
from telebot.types import CallbackQuery
from utils.types import Illust
from utils.db import get_illust

from . import bot, logger
from .util import remove_message_reply_markup_item


@bot.callback_query_handler(func=lambda x: re.match(r"like:\w+:\d+", x.data))
def bookmark_query(query: CallbackQuery):
    expr = query.data[query.data.index(':')+1:]
    logger.debug(query.data)
    logger.debug(expr)
    illust = get_illust(expr)
    logger.info(f"Bookmark query pix:{illust}")
    res = illust.add_bookmark()
    if res is None:
        logger.error(f"Bookmark {illust} error")
        bot.answer_callback_query(query.id, f"{illust.id} 收藏出错")
    else:
        logger.info(f"Bookmark {illust} done")
        
        bot.answer_callback_query(query.id)
        bot.reply_to(query.message, f"{illust.id} 已收藏")
        remove_message_reply_markup_item(query.message, "收藏")
        logger.info(f"Reply markup modified")
    