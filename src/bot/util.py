from typing import *

from telebot import types
from utils import TOKEN
from utils.types import Illust
from utils import retry
from utils.log import with_log
from . import bot, logger, logd


@logd
@retry(times=3)
def send_illust(chatId:int, illust:Illust, reply_to:Optional[int]=None):
    logger.debug(f"Bot 'send_illust' called: {chatId=}, {illust=}")
    markup = types.InlineKeyboardMarkup()
    btnHome = types.InlineKeyboardButton(text="主页", url=illust.home)
    
    if illust.pageCount > 1:
        btnSeeall = types.InlineKeyboardButton(text="全部", callback_data=f"seeall:{illust.region}:{illust.id}")
        markup.row(btnHome, btnSeeall)
        logger.debug(f"{illust.pageCount} pages exist, seeall button added")
    else:
        markup.row(btnHome)
    logger.debug(f"Homepage button added: {btnHome.url}")
    
    if str(chatId) == str(TOKEN['chatid_me']):
        btnBookmark = types.InlineKeyboardButton(text="收藏", callback_data=f'like:{illust.region}:{illust.id}')
        markup.row(btnBookmark)
        logger.debug(f"Message send to 'ME', bookmark button added: {btnBookmark.callback_data}")

    lines = [
        f"{illust.title}" + (f"({illust.pageCount} pages)" if illust.pageCount > 1 else ""),
        "Artist: {}".format(illust.author),
        "Tags: {}".format(', '.join('#' + x for x in illust.authTags)),
        "Level: {}".format(illust.sanityLevel)
    ]
    logger.debug(f"Caption constructed: {lines=}")

    bot.send_photo(chatId, illust.url, caption='\n'.join(lines), 
                   reply_markup=markup, reply_to_message_id=reply_to)
    logger.debug(f"Photo sent: {chatId=}, {illust.url=}")

@logd
@retry(times=3)
def remove_message_reply_markup_item(message:types.Message, markup_item:str) -> None:
    logger.debug(f"Bot 'remove_message_reply_markup_item' called: {message.id=}, {markup_item=}")
    markup = message.reply_markup.to_dict()
    newMarkup = types.InlineKeyboardMarkup()
    for line in markup["inline_keyboard"]:
        newMarkup.row(*(types.InlineKeyboardButton.de_json(x) for x in line if x["text"] != markup_item))
    logger.debug(f"New markup constructed")
    bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=newMarkup)
    logger.debug(f"markup edited")

@logd
@retry(times=3)
def send_message(*args, **kwargs) -> None:
    bot.send_message(*args, **kwargs)