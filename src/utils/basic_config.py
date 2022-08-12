import logging
import os
import sys
from typing import *
import os

from utils import CONFIG

BASE_FMT = logging.Formatter("{asctime} - {levelname}: {message}", style="{", datefmt="%Y/%m/%d %H:%M:%S")
MODULE_FMT = logging.Formatter("{asctime} - {levelname}: [{name}] {message}",  style="{", datefmt="%Y/%m/%d %H:%M:%S")

def get_config() -> Dict[str, Any]:
    return CONFIG

def get_logger(name: str, 
               fileLogLevel=os.environ.get("fll", logging.DEBUG), 
               streamLogLevel=os.environ.get("sll", logging.INFO)) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    os.makedirs(CONFIG["log_path"], exist_ok=True)
    hdlrFile = logging.FileHandler(os.path.join(CONFIG["log_path"], f"{name}.log"))
    hdlrFile.setLevel(fileLogLevel)
    hdlrFile.setFormatter(BASE_FMT)
    logger.addHandler(hdlrFile)
    
    hdlrStream = logging.StreamHandler(stream=sys.stdout)
    hdlrStream.setLevel(streamLogLevel)
    hdlrStream.setFormatter(MODULE_FMT)
    logger.addHandler(hdlrStream)
    
    hdlrAll = logging.FileHandler(os.path.join(CONFIG["log_path"], "main.log"))
    hdlrAll.setLevel(fileLogLevel)
    hdlrAll.setFormatter(MODULE_FMT)
    logger.addHandler(hdlrAll)
    
    return logger