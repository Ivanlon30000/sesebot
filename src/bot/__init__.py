from typing import *
from utils import TOKEN
from utils.basic_config import get_logger

logger = get_logger(__name__)

bot = telebot.TeleBot(TOKEN["bot"])

# # util funcs
# from .utils import *

# import bot functions
from .start import *
from .sese import *
from .bookmark import *
from .seeall import *
from .info import *

# import default response
from .default import *


def run():
    bot.infinity_polling()
    

if __name__ == "__main__":
    run()