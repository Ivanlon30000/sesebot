import json
from typing import *

import pixivpy3
from utils import TOKEN

        
_papi = pixivpy3.AppPixivAPI()

class _PAPI:
    def __init__(self) -> None:
        self.auth()
        
    def __getattribute__(self, name: str) -> Any:
        # self own attri
        # print(name)
        selfattri = {
            "api": _papi,
            "auth": lambda refresh_token=None: _papi.auth(refresh_token=TOKEN["pixiv"] if refresh_token is None else refresh_token),
            "maxTry": 3,
        }
        if name in selfattri:
            return selfattri[name]
        
        # papi attri
        attri = _papi.__getattribute__(name)

        if isinstance(attri, Callable):
            def wraper(*args, **kwargs) -> Any:
                for _ in range(self.maxTry):
                    # try self.maxTry times. If raise PixivError or error in response, do auth then retry
                    flag = True
                    try:
                        result = attri(*args, **kwargs)
                    except PixivError:
                        flag = False
                    else:
                        if isinstance(result, dict) and "error" in result:
                            flag = False
                    
                    if flag:
                        return result
                    else:
                        self.api.auth()
                return None
            return wraper
        else:
            return attri

API = _PAPI()

# functions
def get_agent() -> pixivpy3.AppPixivAPI:
    return API

def refresh_token() -> None:
    API.auth()

# imports
from .aapi import *
from .types import *
