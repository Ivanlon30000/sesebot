import re
from typing import *

from telebot.types import CallbackQuery, InputMediaPhoto
from utils.db import get_illust

from . import bot, logger
from .util import remove_message_reply_markup_item


@bot.callback_query_handler(func=lambda x: re.match(r"seeall:\w+:\d+", x.data))
def seeall_query(query: CallbackQuery):
    logger.info(f"Seeall query received from {query.message.chat.id}: {query.data=}")
    illust = get_illust(query.data[query.data.index(':')+1:])
    urls = illust.illust_image_urls()
    if urls is not None:
        logger.info(f"{len(urls)} for {illust}")
        media = [InputMediaPhoto(url) for url in urls]
        bot.send_media_group(query.message.chat.id, media, reply_to_message_id=query.message.id)
        logger.info(f"Media group sent")
        remove_message_reply_markup_item(query.message, "全部")
        logger.info(f"Reply markup modified")
    else:
        bot.send_message(query.message.chat.id, f"出错力！")
        logger.error(f"Seeall query from {query.message.chat.id} error, {query.data=}")
    bot.answer_callback_query(query.id)
    logger.info(f"Query answer message sent")
       