import logging
import os
import sys
from typing import *
from utils import CONFIG
import redis


BASE_FMT = logging.Formatter("{asctime} - {levelname}: {message}", style="{", datefmt="%Y/%m/%d %H:%M:%S")
MODULE_FMT = logging.Formatter("{asctime} - {levelname}: [{name}] {message}",  style="{", datefmt="%Y/%m/%d %H:%M:%S")

def get_config() -> Dict[str, Any]:
    return CONFIG

def get_logger(name: str, fileLogLevel=logging.DEBUG, streamLogLevel=logging.INFO) -> logging.Logger:
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


def get_database() -> Tuple[redis.client.Redis, Mapping[str, Any]]:
    # database
    REDIS_HOST = CONFIG["db_host"]
    REDIS_PORT = CONFIG["db_port"]
    # logger.info(f"Connecting redis {REDIS_HOST}:{REDIS_PORT}")
    db = redis.Redis(REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    dbinfo = db.info()
    return db, dbinfo
    # logger.info("Redis db connected: {}".format(','.join([f"{k}:{v}" for k, v in dbinfo.items()])))
