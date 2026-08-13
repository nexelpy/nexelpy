from datetime import datetime
from typing import Literal
from .session_proxy.session_middleware import SessionManager
from .request_proxy.requestProxy import request

class CookiesManager:
    def __init__(self):
        super().__init__()
        self._cookies_list =[]

    def set_Cookie(self,*,max_age: int | None = None,expires: datetime | str | int | None = 2678400,path: str | None = "/",domain: str | None = None,
        secure: bool = False,httponly: bool = False,samesite: Literal["lax", "strict", "none"] | None = "lax",partitioned: bool = False,**data,):
        if not data:
            raise ValueError("Cookie need key and value for set")
        for key, value in data.items():
            self._cookies_list.append({"key": key,"value": value,"max_age": max_age,"expires": expires,"path": path,"domain": domain,
                "secure": secure,"httponly": httponly,"samesite": samesite,"partitioned": partitioned,})

    def delete_Cookie(self, *keys: str):
        if not keys:
            keys = tuple(request.cookies.keys())
        for key in keys:
            self._cookies_list.append({"key": key,"value": "","max_age": 0,"expires": "Thu, 01 Jan 1970 00:00:00 GMT","path": "/","domain": None,
                "secure": False,"httponly": False,"samesite": "lax","partitioned": False,})

    def set_Session(self, path="/",secure=True,httponly=True,samesite="strict", max_age=3600 * 24 * 1,**data):
        encrypted = SessionManager.encrypt(data)
        self.set_Cookie(key="n-session",value=encrypted,path=path,secure=secure, httponly=httponly,samesite=samesite,max_age=max_age)

    def _setCookiesFromList(self,response):
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)