from typing import *

import telebot
# from pixiv import PixivIllust
from utils.types import Illust
from telebot import types
from telebot.util import quick_markup
from . import bot, logger

from utils import TOKEN


def send_illust(chatId:int, illust:Illust, reply_to:Optional[int]=None):
    markup = types.InlineKeyboardMarkup()
    btnHome = types.InlineKeyboardButton(text="主页", url=illust.home)
    
    if illust.pageCount > 1:
        btnSeeall = types.InlineKeyboardButton(text="全部", callback_data=f"seeall:{illust.region}:{illust.id}")
        markup.row(btnHome, btnSeeall)
    else:
        markup.row(btnHome)
    
    if str(chatId) == str(TOKEN['chatid_me']):
        btnBookmark = types.InlineKeyboardButton(text="收藏", callback_data=f'like:{illust.region}:{illust.id}')
        markup.row(btnBookmark)

    lines = [
        f"{illust.title}" + (f"({illust.pageCount} pages)" if illust.pageCount > 1 else ""),
        "Artist: {}".format(illust.author),
        "Tags: {}".format(', '.join('#' + x for x in illust.authTags)),
        "Level: {}".format(int(illust.sanityLevel))
    ]

    bot.send_photo(chatId, illust.url, caption='\n'.join(lines), 
                   reply_markup=markup, reply_to_message_id=reply_to)


def remove_message_reply_markup_item(message:types.Message, markup_item:str) -> None:
    markup = message.reply_markup.to_dict()
    #newMarkup = remove_reply_markup_item(markup, markup_item)
    newMarkup = types.InlineKeyboardMarkup()
    for line in markup["inline_keyboard"]:
        newMarkup.row(*(types.InlineKeyboardButton.de_json(x) for x in line if x["text"] != markup_item))

    bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=newMarkup)
