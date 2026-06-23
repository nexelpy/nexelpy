import json
from .pluginBuilder import PluginBuilder
from ..mediator import _Global_nexelpy_var
from starlette.responses import JSONResponse

class Vapi(PluginBuilder):
    def __init__(self, headerConfig=_Global_nexelpy_var.STRICT_GLOBAL_HEADERS):
        super().__init__()
        self.responseHeader = headerConfig

    def RESPONSE(self,**data):
        final_data = {
                "data": data,
                "cssLink":[(self._path_generate(url),attrs) for (url, attrs) in self._css_files] or None, 
                "jsLink":[(self._path_generate(url),attrs) for (url, attrs) in self._js_files] or None, 
                "ntgLink":None,
                "jsCode":None,
                "view": self.elementsContainer.content}

        response = JSONResponse(content= json.dumps(final_data, ensure_ascii=False) ,status_code=200,headers=self.Headers.build_header())
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)
        return response