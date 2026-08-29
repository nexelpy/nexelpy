from .pluginBuilder import PluginBuilder
from starlette.responses import HTMLResponse
from .headTagAnalyzer import HeadTagAnalyzer

class PageBilder(PluginBuilder):
    def __init__(self,file=None,title="Nexelpy",favicon_path="/nexel-venv/static/img/nexel-logo.png",favicon_type="image/png",nextyles=None,):
        super().__init__(file=file,nextyles=None,)

        self.element("meta",parent=self.HEAD_tag,charset="UTF-8",selfClose=True,)
        self.element("meta",parent=self.HEAD_tag,name="viewport",content="width=device-width, initial-scale=1.0",selfClose=True,)
        self.element("title",parent=self.HEAD_tag,text=title,)
        self.element("link",parent=self.HEAD_tag,rel="icon",href=favicon_path,type=favicon_type,selfClose=True,)

        self._add_nextyle_links(nextyles)

    def RESPONSE(self):
        HeadTagAnalyzer(self.HEAD_tag).analyze()
        response = HTMLResponse(content=self.elementsContainer.content,status_code=200,headers=self.Headers.build_header(),media_type="text/html")
        self._setCookiesFromList(response=response)
        return response