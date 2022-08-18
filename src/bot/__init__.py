from typing import *

import telebot
from utils import TOKEN, get_logger


logger = get_logger(__name__)

bot = telebot.TeleBot(TOKEN["bot"])

# import bot functions
from .bookmark import *
from .info import *
from .seeall import *
from .sese import *
from .start import *

# import default response
from .default import *

def run():
    logger.info("Bot running")
    bot.infinity_polling()

