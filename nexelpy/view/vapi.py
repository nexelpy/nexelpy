import json
from .pluginBuilder import PluginBuilder
from starlette.responses import JSONResponse
from .headTagAnalyzer import HeadTagAnalyzer

class Vapi(PluginBuilder):
    def __init__(self, file):
        super().__init__(file=file)
        

    def RESPONSE(self,**data):
        HeadTagAnalyzer(self.HEAD_tag).analyze()
        final_data = {
                "data": data,
                "HEAD_tag":self.HEAD_tag.content,
                "BODY_tag": self.BODY_tag.content}

        response = JSONResponse(content= json.dumps(final_data, ensure_ascii=False) ,status_code=200,headers=self.Headers.build_header())
        self._setCookiesFromList(response=response)
        return response