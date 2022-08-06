from typing import *
from telebot.util import quick_markup
from pixiv import PixivIllust
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