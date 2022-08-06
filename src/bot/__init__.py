from typing import *
from utils.feed import to_photo
from telebot.util import quick_markup


def bot_send_illust(bot, chatId:int, illust:Dict[str, Any], withButton:bool=True, group:str="illust"):
    if withButton:
        markup = quick_markup({
            '收藏': {'callback_data': f'like:{group}:{illust["id"]}'}
        })
    else:
        markup = None
    lines = [
        illust["title"],
        "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
    ]
    if "author" in illust:
        lines.append(f"Artist: {illust['author']}")
    lines.append("Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(','))))
    bot.send_photo(chatId, to_photo(illust["img"]), caption='\n'.join(), reply_markup=markup)