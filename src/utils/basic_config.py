import logging
import os
import sys
from typing import *
from utils import CONFIG
import redis


BASE_FMT = "{asctime} [{levelname}]\t{message}"

def get_config() -> Dict[str, Any]:
    return CONFIG

def get_logger(name: str, fileLogLevel=logging.DEBUG, streamLogLevel=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    os.makedirs(CONFIG["log_path"], exist_ok=True)
    hdlrFile = logging.FileHandler(
        os.path.join(CONFIG["log_path"], f"{name}.log"))
    hdlrFile.setLevel(logging.DEBUG)
    hdlrFile.setFormatter(logging.Formatter(
        fmt=BASE_FMT, style="{", datefmt="%Y/%m/%d %H:%M:%S"))

    hdlrStream = logging.StreamHandler(stream=sys.stdout)
    hdlrStream.setLevel(logging.INFO)
    hdlrStream.setFormatter(logging.Formatter(
        fmt="{name: >16s} - "+BASE_FMT, style="{", datefmt="%Y/%m/%d %H:%M:%S"))

    logger.addHandler(hdlrFile)
    logger.addHandler(hdlrStream)
    
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
