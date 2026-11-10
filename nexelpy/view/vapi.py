from .pluginBuilder import PluginBuilder
from starlette.responses import JSONResponse
from .headTagAnalyzer import HeadTagAnalyzer

class Vapi(PluginBuilder):
    def __init__(self, file):
        super().__init__(file=file)
        

    def RESPONSE(self,status_code=200,status_message="",**data):
        HeadTagAnalyzer(self.headTag).analyze()
        final_data = {
                **data ,
                "QE_links_header":self.HEAD_tag.content,
                "view": self.bodyTag.content,
                "status_message":status_message,
                }

        response = JSONResponse(content=final_data, status_code=status_code , headers=self.Headers.build_header())
        self._setCookiesFromList(response=response)
        self._set_csrf_cookie_and_header(response)
        return response