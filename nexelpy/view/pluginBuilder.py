from .formBuilder import FormBuilder
from ..mediator.reDirect import redirect_now
from urllib.parse import urlencode
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from .pathBuilder import PathBuilder
from ..mediator.cookiesManager import CookiesManager
# from .quickEvents.quickEventsBuilder import QuickEvents

class PluginBuilder(FormBuilder,CookiesManager): 
    def __init__(self,file=None):
        super().__init__()
        self._plugin_return_func_data = None
        self.Headers = HeaderBuilder()
        self._PathBuilder = PathBuilder(file_path=file,root=self.REQUEST._get_original_request().app.root_Path)
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

    def URLs(self,url):
        return self._PathBuilder.URLs(url=url)
    
    def redirect(self, url: str, status_code: int = 307, **kwargs):
        if kwargs:
            params = {key: value for key, value in kwargs.items() if value is not None}
            if params:
                separator = "&" if "?" in url else "?" 
                url = f"{url}{separator}{urlencode(params, doseq=False)}"
        redirect_now(url=url, status_code=status_code)


    def RESPONSE(self,*arg):
        self._plugin_return_func_data = arg
        return self 