import re
from typing import *

from telebot.types import CallbackQuery
from utils.db import get_illust

from . import bot, logger
from .util import remove_message_reply_markup_item


@bot.callback_query_handler(func=lambda x: re.match(r"like:\w+:\d+", x.data))
def bookmark_query(query: CallbackQuery):
    logger.info(f"Bookmark query received from {query.message.chat.id}: {query.data=}")
    illust = get_illust(query.data[query.data.index(':')+1:])
    logger.info(f"Illust instance created: {illust}")
    res = illust.add_bookmark()
    if res is None:
        logger.error(f"Bookmark {illust} error")
        bot.answer_callback_query(query.id, f"{illust} 收藏出错")
        logger.error(f"Error message sent")
    else:
        logger.info(f"Bookmark {illust} done")
        bot.answer_callback_query(query.id)
        bot.reply_to(query.message, f"{illust.id} 已收藏")
        logger.info(f"Reply message sent")
        remove_message_reply_markup_item(query.message, "收藏")
        logger.info(f"Reply markup modified")
    