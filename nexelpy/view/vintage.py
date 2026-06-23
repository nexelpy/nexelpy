import os
from typing import Any
from .pluginBuilder import PluginBuilder
from ..mediator.request_proxy.request_object import get_request
from starlette.templating import Jinja2Templates
from starlette.responses import Response
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder
from ..mediator.request_proxy.requestProxy import request

class Vintage(PluginBuilder):
    def __init__(self,):
        super().__init__()
        self.REQUEST = request
        self.Headers = HeaderBuilder()

    def RESPONSE(self, html_path: str, **data: Any) -> Response:
        templates = Jinja2Templates(directory=html_path)
        response = templates.TemplateResponse(request=request,name=templates,context=data,headers=self.Headers.build_header())

        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)

        return response