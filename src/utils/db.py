import os
import random
import re
from typing import *

import redis

from utils import CONFIG, TOKEN
from utils.basic_config import get_logger
from utils.types import Illust


logger = get_logger(__name__)

REDIS_HOST = CONFIG["db_host"]
REDIS_PORT = CONFIG["db_port"]
_db = redis.Redis(REDIS_HOST, port=REDIS_PORT, decode_responses=True)
class _DDB:
    def __getattribute__(self, __name: str) -> Any:
        attri = _db.__getattribute__(__name)
        if isinstance(attri, Callable):
            def warp(*args, **kwargs) -> Any:
                result = attri(*args, **kwargs)
                logger.debug(f"\n\t{__name}(*{args}, **{kwargs}) \n\t -> ({type(result)}){result}")
                return result
            return warp
        else:
            return attri
db: redis.Redis = _DDB() if os.environ.get("DEVELOP", False) else _db


# funcs
def get_database() -> Tuple[redis.client.Redis, Mapping[str, Any]]:
    return db, None


def get_illust(illustId:int | str, group:str="illust") -> Illust | None:
    res = db.hgetall(f"{group}:{illustId}") 
    if res:
        return Illust.from_db(res)
    else:
        return 


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
def query_all_illusts_id(chatId:int, group:str, applySanity:bool) -> List[str]:
    """查询所有图片的id

    Args:
        chatId (int):  
        group (str): 
        applySanity (bool): 是否应用sanity过滤.

    Returns:
        List[str]: 
    """
    imglist = [x.split(':')[-1] for x in db.keys(f"{group}:*")]
    userSeen = db.smembers(f"user_seen:{chatId}")
    userLevel = db.hget("sanityLevel", chatId)
    if userLevel:
        userLevel = userLevel.split(',')
    else:
        userLevel = ['0', '2', '4', '6']
    logger.info(f"user {chatId} level: {userLevel}")
    result = []
    for illustId in imglist:
        if illustId in userSeen:
            continue
        
        if applySanity:
            illustLevel = db.hget(f"{group}:{illustId}", "sanityLevel")
            if not illustLevel:
                continue
            if illustLevel not in userLevel:
                continue
        
        result.append(illustId)
    return result


def feed_all_interactive(chatId:int, group:str, applySanity:bool=False) -> Generator[Illust | int, None, None]:
    """所有图片（交互式）
    函数返回值是一个生成器，生成器迭代的第一个值是整数，表示符合条件的图片的数量
    若数量>0，接下来迭代的是Illust
    否则停止迭代
    
    e.g.
    ```python
    feed = feed_all_interactive(chatId, group)
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
        group (str): 
        applySanity (bool, optional): 是否应用sanity过滤. Defaults to False.

    Yields:
        Generator[Illust | int, None, None]: 
    """
    imglist = query_all_illusts_id(chatId, group, applySanity=applySanity)
    yield len(imglist)
    if len(imglist) > 0:
        for illustId in imglist:
            dbDict = db.hgetall(f"{group}:{illustId}")
            illust = Illust.from_db(dbDict)
            db.sadd(f"user_seen:{chatId}", illustId)
            yield illust

   
def feed_all(chatId:int, group:str, applySanity:bool=False) -> Generator[Illust, None, None]:
    feed = feed_all_interactive(chatId, group, applySanity=applySanity)
    if feed.__next__():
        for illust in feed:
            yield illust
    else:
        raise StopIteration()
    

def random_feed_interactive(chatId:int, group:str="illust", applySanity:bool=True) -> Generator[Illust | bool, None, None]:
    """随机返回图片（交互式）
    函数返回值是一个生成器，生成器迭代的第一个值是bool类型，表示是否有剩余图片
    若True，接下来迭代的是Illust
    否则停止迭代
    
    e.g.
```python
    feed = random_feed_interactive(chatId, group)
    num = feed.__next__()
    if num:
        print(illust.id)
    else:
        print("没有图片")
```
    Args:
        chatId (int): 
        group (str, optional): 图片所属组别. Defaults to "illust".
        applySanity (bool, optional): 是否应用sanity过滤. Defaults to True.

    Yields:
        Generator[Illust | bool, None, None]: 
    """
    imglist = query_all_illusts_id(chatId, group, applySanity=applySanity)
    if len(imglist) > 0:
        yield True
        illustId = random.choice(imglist)
        logger.info("Image {} selected".format(illustId))
        illust = Illust.from_db(db.hgetall(f"{group}:{illustId}"))
        db.sadd(f"user_seen:{chatId}", illustId)
        yield illust
    else:
        yield False


def random_feed(chatid:int, group:str="illust", applySanity:bool=True) -> Optional[Illust]:
    feed = random_feed_interactive(chatid, group, applySanity=applySanity)
    res = feed.__next__()
    if res:
        return feed.__next__()
    else:
        return None

