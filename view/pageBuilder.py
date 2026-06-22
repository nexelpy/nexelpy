from .pluginBuilder import PluginBuilder
from ..mediator import _Global_nexelpy_var
from starlette.responses import HTMLResponse


class PageBilder(PluginBuilder):
    def __init__(self,title="Nexelpy", favicon_path="root/static/favicon.png",favicon_type="image/png"):
        super().__init__()
        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.HTML = self.element("html", parent=self.elementsContainer)

        # head
        self.HEAD = self.element("head", parent=self.HTML)
        self.element("meta", parent=self.HEAD, charset="UTF-8", selfClose=True)
        self.element("meta", parent=self.HEAD, name="viewport", content="width=device-width, initial-scale=1.0", selfClose=True)
        self.element("title", parent=self.HEAD, text=title)
        self.element("link", parent=self.HEAD, rel="icon", href=favicon_path, type=favicon_type, selfClose=True)

        self.STYLE = self.element("style",parent=self.HTML)
        # body
        self.BODY = self.element("body", parent=self.HTML)

    def default_parent(self):#this method override parentResolverBase.default_parent()
        return self.BODY
    
    def RESPONSE(self):
        [self.link(parent=self.HEAD, href= url , **attrs) for (url, attrs) in self._css_files]
        [self.script(parent=self.HEAD, src= url , **attrs) for (url, attrs) in self._js_files]

        response = HTMLResponse(content=self.elementsContainer.content,status_code=200,headers=self.Headers.build_header( ),media_type="text/html")
        
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)
        return response