from .formBuilder import FormBuilder
from ..mediator.reDirect import redirect_now
from urllib.parse import urlencode
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from .pathBuilder import PathBuilder
from ..mediator.cookiesManager import CookiesManager
import base64
import hashlib
# from .quickEvents.quickEventsBuilder import QuickEvents

class PluginBuilder(FormBuilder, CookiesManager):
    def __init__(self, file=None, nextyles=None,nexcripts=None):
        super().__init__()
        self._plugin_return_func_data = None
        self.Headers = HeaderBuilder()
        self._file = file
        self._root_path = self.REQUEST._get_original_request().app.root_Path
        self._PathBuilder = PathBuilder(file_path=file, root=self._root_path)
        self._scope_token = self._make_scope_token()

        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.HTML_tag = self.element("html", parent=self.elementsContainer)
        self.HEAD_tag = self.element("head", parent=self.HTML_tag)
        self.BODY_tag = self.element("body", parent=self.HTML_tag)
       


    # def _add_nextyle_link(self, nextyle, default_parent=None):
    #     if nextyle is not None:
    #         attrs = getattr(nextyle, "_tag_attrs", {}).copy()
    #         parent = attrs.pop("parent", default_parent or self.HEAD_tag)
    #         self.element("link", parent=parent, rel="stylesheet", href=nextyle.href, selfClose=True, **attrs)

    # def _add_nexcript_script(self, nexcript, default_parent=None):
    #     if nexcript is not None:
    #         attrs = getattr(nexcript, "_tag_attrs", {}).copy()
    #         parent = attrs.pop("parent", default_parent or self.HEAD_tag)
    #         self.element("script", parent=parent, src=nexcript.src, **attrs)

    def scoping(self, text="", props="", parent=None, **attributes):
        attributes["data-scoping"] = self._scope_token
        return self.element(tagName="div", text=text, props=props, parent=parent, **attributes)

    def _make_scope_token(self) -> str:
        digest = hashlib.blake2s(str(self._file).encode("utf-8"), digest_size=4).digest()
        return base64.b32encode(digest).decode("ascii").lower().rstrip("=")[:5]


    async def importPlugin(self, plugin, parent=None):
        PARENT = self._setParent(parent)
        PLUGIN = await plugin
        PARENT.children.extend(PLUGIN.BODY_tag.children)
        self.HEAD_tag.children.extend(PLUGIN.HEAD_tag.children)
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