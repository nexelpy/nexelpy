from .pluginBuilder import PluginBuilder
from starlette.responses import HTMLResponse


class PageBilder(PluginBuilder):
    def __init__(self,title="Nexelpy", favicon_path="",favicon_type="image/png"):
        super().__init__()
        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.HTML_tag = self.element("html", parent=self.elementsContainer)

        # head
        self.HEAD_tag = self.element("head", parent=self.HTML_tag)
        self.element("meta", parent=self.HEAD_tag, charset="UTF-8", selfClose=True)
        self.element("meta", parent=self.HEAD_tag, name="viewport", content="width=device-width, initial-scale=1.0", selfClose=True)
        self.element("title", parent=self.HEAD_tag, text=title)
        self.element("link", parent=self.HEAD_tag, rel="icon", href=favicon_path, type=favicon_type, selfClose=True)

        self.STYLE_tag = self.element("style",parent=self.HTML_tag)
        # body
        self.BODY_tag = self.element("body", parent=self.HTML_tag)

    def default_parent(self):#this method override parentResolverBase.default_parent()
        return self.BODY_tag
    
    def RESPONSE(self):
        [self.link(parent=self.HEAD_tag, href=href, **attrs) for href, attrs in self._css_files.items()]
        [self.script(parent=self.HEAD_tag, src=src, **attrs) for src, attrs in self._js_files.items()]

        exQE = self.QuickEvents.export # export current QE 
        if exQE:
            self.script(text=exQE,type="module")
        if self._QE_objects: # export QE of other plugin
            for i in self._QE_objects:
                self.script(text=i.export,type="module")

        response = HTMLResponse(content=self.elementsContainer.content,status_code=200,headers=self.Headers.build_header(),media_type="text/html")
        
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)
        return response