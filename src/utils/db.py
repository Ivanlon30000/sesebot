"""
与数据库交互的模块
"""

import random
import re
from time import time
from typing import *

import redis

from utils import CONFIG, TOKEN
from utils.basic_config import get_logger
from utils.region_map import MAP
from utils.types import Illust

logger = get_logger(__name__)

REDIS_HOST = CONFIG["db_host"]
REDIS_PORT = CONFIG["db_port"]
_db = redis.Redis(REDIS_HOST, port=REDIS_PORT, decode_responses=True)
class _DDB:
    """对数据库接口封装，用于debug
    """
    def __getattribute__(self, __name: str) -> Any:
        attri = _db.__getattribute__(__name)
        if isinstance(attri, Callable):
            def warp(*args, **kwargs) -> Any:
                logger.debug(f"{__name}(*{args}, **{kwargs})")
                result = attri(*args, **kwargs)
                logger.debug(f" -> ({type(result)}){result}")
                return result
            return warp
        else:
            return attri
db: redis.Redis = _DDB()


# funcs
def get_database() -> Tuple[redis.Redis, None]:
    return db, None


def get_illust(expr:str|None=None, region:str|None=None, illustId:str|int|None=None) -> Illust | None:
    """从数据库中读取illust并自动判断类型(定义于utils.region_map)
    
    Returns:
        Illust | None: Illust的子类
    """
    logger.debug(f"Get illust: {expr=}, {region=}, {illustId=}")
    if expr is not None:
        if not expr.startswith("illust:"):
            expr = "illust:"+expr
        _, region, illustId = expr.split(":")
    elif region is not None and illustId is not None:
        pass
    else:
        raise ValueError("'region' and 'illustId' must be given while 'expr' not given")

    res = db.hgetall(f"illust:{region}:{illustId}")
    if res:
        cls = MAP[region]
        result = cls.from_db(res)
        logger.debug(f"{cls.__class__} instance, type {type(result)}")
    else:
        result = None
        
    logger.debug(f"Returns {result}")
    return result


def get_sanity_level(chatId:int | str) -> List[int]:
    res = db.hget("sanityLevel", chatId)
    if res:
        return res.split(',')
    else:
        return []

def set_sanity_level(chatId:int | str, expr:List[int|str]|str) -> List[str]:
    """设置sanity level

    Args:
        chatId (int | str):
        expr (List[int|str]|str): 字符串表达式自动转换为列表，支持
            1) 纯数字 '2' -> ['2']
            2) ','连接符 '2,4,6' -> ['2', '4', '6']
            3) '-'连接符 '-6' -> ['0', '2', '4', '6'], '4-6' -> ['4', '6']

    Returns:
        bool: 新sanity level
    """
    if isinstance(expr, list):
        newLevel = (str(x) for x in expr)
    elif isinstance(expr, str):
        mat = re.match(r"(\d(,\d)*|\d?-\d?)$", expr)
        if mat:
            expr = mat.group(1)
            if '-' in expr:
                s, e = expr.split('-')
                s = int(s) if s else 0
                e = int(e) if e else 6
                newLevel = (str(x) for x in range(s, e+1, 2))
            else:
                newLevel = expr.split(',')
        else:
            newLevel = [] 
    elif isinstance(expr, int):
        newLevel = {str(expr)}
    else:
        raise ValueError(f"Param 'sanityLevel' type error")
    newLevel = ','.join(x for x in set(x for x in newLevel if x in {'0', '2', '4', '6'}))
    if newLevel:
        db.hset("sanityLevel", chatId, newLevel)
    return newLevel


# TODO: 格式化sanity level
def query_all_illusts_key(chatId:int|None, region:str, applySanity:bool|None) -> List[str]:
    """查询所有图片的key (e.g. pixiv:1234567)

    Args:
        chatId (int|None):  
        region (str): 
        applySanity (bool): 是否应用sanity过滤.

    Returns:
        List[str]: 
    """
    logger.debug(f"Query all illusts: {chatId=}, {region=}, {applySanity=}")
    illustKeys = [x[x.index(':')+1:] for x in db.keys(f"illust:{region}:*")]
    logger.debug(f"{len(illustKeys)} illusts exist")
    if chatId is None:
        return illustKeys
    userSeen = db.smembers(f"user_seen:{chatId}")
    userLevel = db.hget("sanityLevel", chatId)
    if userLevel:
        userLevel = userLevel.split(',')
    else:
        userLevel = ['0', '2', '4', '6']
    logger.debug(f"User {chatId} sanity level: {userLevel}")
    
    result = []
    for illustKey in illustKeys:
        if illustKey in userSeen:
            continue
        
        if applySanity:
            illustLevel = db.hget(f"illust:{illustKey}", "sanityLevel")
            if not illustLevel:
                continue
            if illustLevel not in userLevel:
                continue
        
        result.append(illustKey)
    logger.debug(f"Returns {len(result)} illusts")
    return result


def feed_all_interactive(chatId:int, region:str, applySanity:bool=False) -> Generator[Illust | int, None, None]:
    """所有图片（交互式）
    函数返回值是一个生成器，生成器迭代的第一个值是整数，表示符合条件的图片的数量
    若数量>0，接下来迭代的是Illust
    否则停止迭代
    
    e.g.
    ```python
    feed = feed_all_interactive(chatId, region)
    num = feed.__next__()
    if num > 0:
        print(f"有{num}"张图片)
        for illust in feed:
            print(f"Illust id {illust.id}")
    else:
        print("没有图片")
    ```

    Args:
        chatId (int): 
        region (str): 
        applySanity (bool, optional): 是否应用sanity过滤. Defaults to False.

    Yields:
        Generator[Illust | int, None, None]: 
    """
    illustKeys = query_all_illusts_key(chatId, region, applySanity=applySanity)
    yield len(illustKeys)
    if len(illustKeys) > 0:
        for illustKey in illustKeys:
            illust = get_illust(illustKey)
            db.sadd(f"user_seen:{chatId}", illustKey)
            yield illust

   
def feed_all(chatId:int, region:str, applySanity:bool=False) -> Generator[Illust, None, None]:
    feed = feed_all_interactive(chatId, region, applySanity=applySanity)
    if feed.__next__():
        for illust in feed:
            yield illust
    else:
        raise StopIteration()
    

def random_feed_interactive(chatId:int, region:str="*", applySanity:bool=True) -> Generator[Illust | bool, None, None]:
    """随机返回图片（交互式）
    函数返回值是一个生成器，生成器迭代的第一个值是bool类型，表示是否有剩余图片
    若True，接下来迭代的是Illust
    否则停止迭代
    
    e.g.
```python
    feed = random_feed_interactive(chatId, region)
    num = feed.__next__()
    if num:
        print(illust.id)
    else:
        print("没有图片")
```
    Args:
        chatId (int): 
        region (str, optional): 图片所属组别. Defaults to "illust".
        applySanity (bool, optional): 是否应用sanity过滤. Defaults to True.

    Yields:
        Generator[Illust | bool, None, None]: 
    """
    logger.debug(f"Random feed illust: {chatId=}, {region=}, {applySanity=}")
    illustKeys = query_all_illusts_key(chatId, region=region, applySanity=applySanity)
    if len(illustKeys) > 0:
        yield True
        illustKey = random.choice(illustKeys)
        logger.debug(f"Image {illustKey} selected")
        illust = get_illust(illustKey)
        db.sadd(f"user_seen:{chatId}", illustKey)
        yield illust
    else:
        yield False


def random_feed(chatid:int, region:str="*", applySanity:bool=True) -> Optional[Illust]:
    feed = random_feed_interactive(chatid, region, applySanity=applySanity)
    res = feed.__next__()
    if res:
        return feed.__next__()
    else:
        return None


def add_illust(illust:Illust, expire:int|None) -> int | None:
    dumpdata = {**illust.dump(), "recordtime": int(time()*1000)}
    result = db.hset(f"illust:{illust.region}:{illust.id}", mapping=dumpdata)
    if expire and expire > 0:
        db.expire(f"illust:{illust.region}:{illust.id}", expire)
    logger.debug(f"Call add_illust({illust=}, {expire=}) -> {result}")
    return result


def get_recordtime(illust_or_expr:Illust|str) -> int | None:
    """查询illust入库时间

    Args:
        illust (Illust | int): Illust对象或数据库key

    Returns:
        int | None: 
    """
    logger.debug(f"Call get_recordtime({illust_or_expr=}):")
    if isinstance(illust_or_expr, str):
        expr = illust_or_expr if illust_or_expr.startswith("illust:") else "illust:"+illust_or_expr
    else:
        expr = f"illust:{illust_or_expr.region}:{illust_or_expr.id}"
    logger.debug(f"Parsed {expr=}")
        
    result = db.hget(expr)
    logger.debug(f"Returns {result}")
    if result:
        return int(result)
    else:
        return None