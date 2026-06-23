import os
from typing import Any
from .pluginBuilder import PluginBuilder
from ..mediator import _Global_nexelpy_var
from ..mediator.request_proxy.request_object import get_request
from starlette.templating import Jinja2Templates
from starlette.responses import Response

class Vintage(PluginBuilder):
    def __init__(self, headerConfig: dict[str, str] = _Global_nexelpy_var.STRICT_GLOBAL_HEADERS):
        super().__init__()
        self.responseHeader = headerConfig

    def RESPONSE(self, html_path: str, **data: Any) -> Response:
        full_path = self._resolve_file_path(html_path)
        template_dir = os.path.dirname(full_path)
        template_name = os.path.basename(full_path)

        templates = Jinja2Templates(directory=template_dir)
        request = get_request()
        response = templates.TemplateResponse(request=request,name=template_name,context=data,headers=self.responseHeader)

        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)

        return response