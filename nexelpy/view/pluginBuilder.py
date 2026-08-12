from .formBuilder import FormBuilder
from ..mediator.reDirect import redirect_now
from urllib.parse import urlencode
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from ..mediator.session_proxy.session_middleware import SessionManager
from datetime import datetime
from typing import Literal
# from .quickEvents.quickEventsBuilder import QuickEvents

class PluginBuilder(FormBuilder): 
    def __init__(self):
        super().__init__()
        self._plugin_return_func_data = None
        self._cookies_list =[]
        self.Headers = HeaderBuilder()
        # self.QuickEvents = QuickEvents()

        #DOM
        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.HTML_tag = self.element("html", parent=self.elementsContainer)
        self.HEAD_tag = self.element("head", parent=self.HTML_tag)
        self.BODY_tag = self.element("body", parent=self.HTML_tag)

    async def importPlugin(self, plugin, parent=None):
        PARENT = self._setParent(parent)
        PLUGIN = await plugin
        PARENT.children.extend(PLUGIN.BODY_tag.children)
        self.HEAD_tag.children.extend(PLUGIN.HEAD_tag.children)
        self._cookies_list.extend(PLUGIN._cookies_list)
        return PLUGIN._plugin_return_func_data[0] if len(PLUGIN._plugin_return_func_data) ==1 else PLUGIN._plugin_return_func_data 


    def redirect(self, url: str, status_code: int = 307, **kwargs):
        if kwargs:
            params = {key: value for key, value in kwargs.items() if value is not None}
            if params:
                separator = "&" if "?" in url else "?" 
                url = f"{url}{separator}{urlencode(params, doseq=False)}"
        redirect_now(url=url, status_code=status_code)

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

    def RESPONSE(self,*arg):
        self._plugin_return_func_data = arg
        return self 