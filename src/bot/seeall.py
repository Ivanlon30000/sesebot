import re
from typing import *

from telebot.types import CallbackQuery, InputMediaPhoto

import utils

from . import bot, logger
from .util import remove_message_reply_markup_item


@bot.callback_query_handler(func=lambda x: re.match(r"seeall:\d+", x.data))
def seeall_query(query: CallbackQuery):
    _, illustId = query.data.split(":")
    # urls = illust_image_urls(iid)
    urls = utils.pixiv.illust_image_urls(illustId)
    if urls is not None:
        logger.info(f"Sending {illustId} all images")
        media = [InputMediaPhoto(url) for url in urls]
        bot.send_media_group(query.message.chat.id, media, reply_to_message_id=query.message.id)
        logger.info(f"{len(urls)} images sent")
        remove_message_reply_markup_item(bot, query.message, "全部")
        logger.info(f"Reply markup modified")
    else:
        bot.send_message(query.message.chat.id, f"出错力！")
    bot.answer_callback_query(query.id)
       