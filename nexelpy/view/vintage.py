from typing import Any
from starlette.templating import Jinja2Templates
from starlette.responses import Response
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from ..mediator.request_proxy.requestProxy import request
from ..mediator.cookiesManager import CookiesManager
from .pathBuilder import PathBuilder

class Vintage(CookiesManager):
    def __init__(self,file):
        super().__init__()
        self.REQUEST = request
        self.Headers = HeaderBuilder()
        self._PathBuilder = PathBuilder(file_path=file,root=self.REQUEST._get_original_request().app.root_Path)

    def RESPONSE(self, html_path: str, **data: Any) -> Response:
        html = self._PathBuilder._resolve_file_path(html_path)
        templates = Jinja2Templates(directory=html)
        response = templates.TemplateResponse(request=request,name=templates,context=data,headers=self.Headers.build_header())
        self._setCookiesFromList(response=response)
        return response