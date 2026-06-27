from datetime import datetime
from typing import Literal
import json
from ..mediator.session_proxy.session_middleware import SessionManager

class SetCookieSession:
    def __init__(self):
        super().__init__()
        self._cookies_list =[]

    def set_Cookie(self,
                   key: str,
                   value: str = "",
                   max_age: int | None = None,
                   expires: datetime | str | int | None = None,path: str | None = "/",
                   domain: str | None = None,
                   secure: bool = False,httponly: bool = False,
                   samesite: Literal["lax", "strict", "none"] | None = "lax",partitioned: bool = False):
        self._cookies_list.append({"key":key,"value":value,"max_age":max_age,"expires":expires,"path":path,"domain":domain,"secure":secure,"httponly":httponly,"samesite":samesite,"partitioned":partitioned })


    def set_session(self, path="/",secure=True,httponly=True,samesite="strict", max_age=3600 * 24 * 1,**data):
        encrypted = SessionManager.encrypt(data)
        self.set_Cookie(key="n-session",value=encrypted,path=path,secure=secure, httponly=httponly,samesite=samesite,max_age=max_age)