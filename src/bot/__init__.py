from typing import *
from utils.feed import to_photo
from telebot.util import quick_markup


def bot_send_illust(bot, chatId:int, illust:Dict[str, Any], withButton:bool=True):
    if withButton:
        markup = quick_markup({
            '收藏': {'callback_data': 'like:'+illust["id"]}
        })
    else:
        markup = None
    bot.send_photo(chatId, to_photo(illust["img"]), caption='\n'.join([
        illust["title"],
        "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
        "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
    ]), reply_markup=markup)