from functools import wraps
from typing import *

from .const import CONFIG, TOKEN
from .log import get_logger
import time

class JudgeFailedException(Exception):
    pass


def retry(times:int=3, judge:Callable[[Any], bool]|None=None, 
          callback:Callable[[bool, List[Tuple[Any, Optional[Exception]]]], Any]|None=None, 
          ignore:bool=False, wait:float=0):
    """“重试”装饰器
    被装饰的函数重试至多 `times` 次
    
    当 `judge` 不为 `None` 时，被装饰函数的返回结果作为输入参数传入 `judge`，
        `judge` 返回值为 `True` 表示被执行函数执行成功，返回 `False` 则会抛出 `JudgeFailedException`
    当 `judge` 为 `None` 时，被装饰函数未出现能被捕获的错误视为执行成功
    
    当 `callback` 不为 `None` 时，被装饰函数的执行结果传入 `callback`
    
    当 `ignore` 为 `True` 时，被装饰函数执行时的可被捕获的错误不会上报

    Args:
        times (int, optional): 最多重试的次数. Defaults to 3.
        judge (Callable[[Any], bool], optional): 判断函数. Defaults to None.
        callback (Callable[[bool, List[Tuple[Any, Optional[Exception]]]], optional): 回调函数，格式为
```
def callback_function(isSuccess:bool, results:List[Tuple[Any, Optional[Exception]]]) -> None:
    print(f"{isSuccess} 表示被装饰函数在 `times` 次内是否执行成功")
    for i, result in enumerate(results):
        print(f"`results` 的元素是二元组，{result[0]} 和 {result[1]} 分别是被装饰函数"
            f"第 {i} 次的返回值和抛出的错误，如果是 `judge` 返回 `False`，则是`JudgeFailedException`")
```
    Returns:
        Callable: 
    """
    assert isinstance(times, int) and times > 0
    def decorator(func):
        @wraps(func)
        def __retry_func(*args, **kwargs):
            execResults = []
            successFlag = False
            
            for i in range(times):
                result = None
                exception = None
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e
                else:
                    if judge is None or judge(result):
                        successFlag = True
                    else:
                        exception = JudgeFailedException()
                finally:
                    execResults.append((result, exception))
                
                if successFlag:
                    break
                
                if wait > 0:
                    time.sleep(wait)
                    
            if callback is not None:
                callback(successFlag, execResults)
                
            if successFlag:
                return result
            else:
                if ignore:
                    return None
                else:
                    raise execResults[-1][1]
        return __retry_func
    return decorator
