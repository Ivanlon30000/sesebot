import base64
import random
from io import BytesIO
from traceback import format_exc
from typing import *

import telebot
from telebot.types import *

from utils import get_config, get_database, get_logger
from utils.feed import random_feed_interactive, to_photo


CONFIG = get_config()
logger = get_logger(__name__ if __name__ != "__main__" else __file__)

logger.info("Connecting Redis db: {}:{}".format(
    CONFIG["db_host"], CONFIG["db_port"]))
db, _ = get_database()
logger.info("Redis db connected")

with open("token.json") as fp:
    _token = json.load(fp)

bot = telebot.TeleBot(_token["bot"])

@bot.message_handler(commands=["start", "help"])
def start(message: Message):
    bot.reply_to(message, "说，你想涩涩")

@bot.message_handler(regexp=r"(se|色|涩){2}|(se|色|涩)(图|tu)")
def sese(message: Message):
    logger.debug(f"Receive msg: {message}")
    chat_id = message.chat.id
    # try:
    #     logger.debug(f"Receive msg: {message}")
    #     chat_id = message.chat.id
    #     imglist = [x.split(':')[-1] for x in db.keys("illust:*")]
    #     logger.debug(f"Image list: {imglist}")
    #     user_seen = db.smembers(f"user_seen:{message.chat.id}")
    #     imglist = [x for x in imglist if x not in user_seen]
    #     logger.info("{} images available for {}".format(len(imglist), chat_id))
    #     if len(imglist) > 0:
    #         bot.reply_to(message, "涩图来力！")
    #         illustId = random.choice(imglist)
    #         logger.info("Image {} selected".format(illustId))
    #         illust = db.hgetall(f"illust:{illustId}")
    #         if illust["img"].startswith("http"):
    #             photo = illust["img"]
    #         else:
    #             photo = BytesIO(base64.b64decode(illust["img"]))
    #         caption = '\n'.join([
    #             illust["title"],
    #             "Pixiv: https://www.pixiv.net/artworks/{}".format(illustId),
    #             "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
    #         ])
    #         pmsg = bot.send_photo(message.chat.id, photo=photo, caption=caption)
    #         logger.info("Image sent.")
    #         logger.debug(f"Sent msg: {message}")
    #         db.sadd(f"user_seen:{message.chat.id}", illustId)
    #     else:
    #         logger.info("No image available.")
    #         bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
    #         bot.send_message(message.chat.id, "还要涩涩？还要涩涩？还要涩涩？")
    # except Exception as e:
    #     logger.error(format_exc())
    #     bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
    #     bot.send_message(message.chat.id, "不可以涩涩！")
    # else:
    #     return
    feed = random_feed_interactive(db, chat_id)
    if feed.__next__():
        bot.reply_to(message, "涩图来力！")
        illust = feed.__next__()
        photo = to_photo(illust["img"])
        caption = '\n'.join([
            illust["title"],
            "Pixiv: https://www.pixiv.net/artworks/{}".format(illust["id"]),
            "Tags: {}".format(', '.join('#' + x for x in illust["authTags"].split(',')))
        ])
        bot.send_photo(message.chat.id, photo=photo, caption=caption)
    else:
        logger.info("No image available.")
        bot.send_sticker(message.chat.id, "CAACAgUAAxkDAAMcYuoPdZi1WU9ph-DxAf7i9d5uIvsAAqIFAAKX3FBXvDeSjH2iYu4pBA")
        bot.send_message(message.chat.id, "还要涩涩？还要涩涩？还要涩涩？")
        

if __name__ == "__main__": 
    logger.info("Bot looping")
    bot.infinity_polling()
