from .pluginBuilder import PluginBuilder
from starlette.responses import HTMLResponse
from .headTagAnalyzer import HeadTagAnalyzer

class PageBilder(PluginBuilder):
    def __init__(self,file=None,title="Nexelpy",favicon_path="/nexel_venv/static/img/nexel-logo.png",favicon_type="image/png",nextyles=None,):
        super().__init__(file=file)

        self.element("meta",parent=self.headTag,charset="UTF-8",selfClose=True,)
        self.element("meta",parent=self.headTag,name="viewport",content="width=device-width, initial-scale=1.0",selfClose=True,)
        self.element("title",parent=self.headTag,text=title,)
        self.element("link",parent=self.headTag,rel="icon",href=favicon_path,type=favicon_type,selfClose=True,)

        # self._add_nextyle_links(nextyles)

    def RESPONSE(self):
        HeadTagAnalyzer(self.headTag).analyze()
        response = HTMLResponse(content=self.elementsContainer.content,status_code=200,headers=self.Headers.build_header(),media_type="text/html")
        self._setCookiesFromList(response=response)
        self._set_csrf_clientSide_cookie_and_header(response)
        return response