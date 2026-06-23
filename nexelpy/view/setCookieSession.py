from datetime import datetime
from typing import Literal
import json
from ..mediator import _Global_nexelpy_var


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

    def set_Session(self, **kw): 
        session_json = json.dumps(kw)
        encrypted_session = _Global_nexelpy_var.FERNET.encrypt(session_json.encode())
        session_value = encrypted_session.decode()
        self.setCookie(key="n-session",value=session_value,path="/",secure=True,httponly=True,samesite="lax",max_age=3600 * 24 * 7)