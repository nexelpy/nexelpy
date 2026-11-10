from .formBuilder import FormBuilder
from ..mediator.reDirect import redirect_now
from urllib.parse import urlencode
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from .pathBuilder import PathBuilder
from ..mediator.cookiesManager import CookiesManager
from ..criptyle.sharedClasses.scopeToken import _make_scope_token


class PluginBuilder(FormBuilder, CookiesManager):
    def __init__(self, file=None):
        super().__init__()
        self._plugin_return_func_data = None
        self.Headers = HeaderBuilder()
        self._file = file
        self._root_path = self.REQUEST._get_original_request().app.root_Path
        self._PathBuilder = PathBuilder(file_path=file, root=self._root_path)
        self._scope_token = _make_scope_token(file)

        # self.raw("<!doctype html>",parent=self.elementsContainer)
        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.htmlTag = self.element("html", parent=self.elementsContainer)
        self.headTag = self.element("head", parent=self.htmlTag)
        self.bodyTag = self.element("body", parent=self.htmlTag)
       

    def scoping(self, text="", props="", parent=None, **attributes):
        attributes["data-scoping"] = self._scope_token
        return self.element(tagName="div", text=text, props=props, parent=parent, **attributes)


    async def importPlugin(self, plugin, parent=None):
        PARENT = self._setParent(parent)
        PLUGIN = await plugin
        PARENT.children.extend(PLUGIN.bodyTag.children)
        self.headTag.children.extend(PLUGIN.headTag.children)
        self._cookies_list.extend(PLUGIN._cookies_list)
        return PLUGIN._plugin_return_func_data[0] if len(PLUGIN._plugin_return_func_data) ==1 else PLUGIN._plugin_return_func_data 

    def url(self,url):
        return self._PathBuilder.url(url=url)
    
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