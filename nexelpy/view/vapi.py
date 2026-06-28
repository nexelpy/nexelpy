import json
from .pluginBuilder import PluginBuilder
from starlette.responses import JSONResponse

class Vapi(PluginBuilder):
    def __init__(self, ):
        super().__init__()
        

    def RESPONSE(self,**data):
        
        css_links = []
        for href, attrs in self._css_files.items():
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            css_links.append(f'<link href="{href}" {attrs_str} />')
        js_scripts = []
        for src, attrs in self._js_files.items():
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            js_scripts.append(f'<script src="{src}" {attrs_str}></script>')

        exQE = self.QuickEvents.export # export current QE 
        if exQE:
            self.script(text=exQE,type="module")

        if self._QE_objects: # export QE of other plugin
            for i in self._QE_objects:
                self.script(text=i.export,type="module")

        final_data = {
                "data": data,
                "css-links" : "".join(css_links),
                "js-links": "".join(js_scripts),
                "view": self.elementsContainer.content
                }

        
        response = JSONResponse(content= json.dumps(final_data, ensure_ascii=False) ,status_code=200,headers=self.Headers.build_header())
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)
        return response