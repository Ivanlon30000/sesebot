from typing import *

from pixiv import PixivIllust
from telebot.types import InlineKeyboardMarkup, Message
from telebot.util import quick_markup
from utils import TOKEN


def bot_send_illust(bot, chatId:int, illust:PixivIllust, 
                    group:str="illust", reply_to:Optional[int]=None):
    markup = {}
    if illust.pageCount > 1:
        markup ["全部"] = {'callback_data': f"seeall:{illust.id}"}
    
    if chatId == TOKEN['chatid_me']:
        markup['收藏'] = {'callback_data': f'like:{group}:{illust.id}'}
    
    if len(markup) > 0:
        markup = quick_markup(markup)
    else:
        markup = None

    lines = [
        illust.title + (f"({illust.pageCount} pages)" if illust.pageCount > 1 else ""),
        "Pixiv: https://www.pixiv.net/artworks/{}".format(illust.id),
        "Artist: {}".format(illust.author),
        "Tags: {}".format(', '.join('#' + x for x in illust.authTags))
    ]

    bot.send_photo(chatId, illust.url, caption='\n'.join(lines), reply_markup=markup, reply_to_message_id=reply_to)
    
def remove_reply_markup_item(bot, message:Message, markup_item:str) -> None:
    markup = message.reply_markup.to_dict()
    newMarkup = {
        inline["text"]: {"callback_data": inline["callback_data"]} for inline in markup["inline_keyboard"][0] if inline["text"] != markup_item
    }
    newMarkup = quick_markup(newMarkup)
    bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=newMarkup)
