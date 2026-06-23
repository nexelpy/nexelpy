from ..mediator.request_proxy.requestProxy import request
from .setCookieSession import SetCookieSession
from .pathBuilder import PathBuilder
import mimetypes
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, JSONResponse,PlainTextResponse,StreamingResponse,Response,RedirectResponse
from typing import AsyncIterable
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder

class RestApi(SetCookieSession,PathBuilder):
    def __init__(self):
        super().__init__()
        self.REQUEST = request
        self.Headers = HeaderBuilder()
    
    def RESPONSEfile(self, type, path, backgroundTask=None, disposition="attachment"):
        response = FileResponse(
            self._resolve_file_path(path),
            status_code=200,
            headers=self.Headers.build_header(),
            media_type= type if "/" in type else mimetypes.guess_type(f"file.{type}")[0],
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
            content_disposition_type=disposition,
        )
        self._set_cookielist_to_response(response)
        return response

    def RESPONSEjason(self,backgroundTask=None, **data):
        response = JSONResponse(
            content=data,
            status_code=200,
            headers=self.Headers.build_header(),
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._set_cookielist_to_response(response)
        return response

    def RESPONSEtext(self, content: str, backgroundTask=None, status_code=200):
        response = PlainTextResponse(
            content=content,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._set_cookielist_to_response(response)
        return response

    def RESPONSEstreaming(self,content: AsyncIterable[str | bytes], type="text/plain", backgroundTask=None, status_code=200):
        response = StreamingResponse(
            content=content,
            status_code=status_code,
            headers=self.Headers.build_header(),
            media_type= type if "/" in type else mimetypes.guess_type(f"file.{type}")[0],
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._set_cookielist_to_response(response)
        return response

    def RESPONSEnoContent(self, backgroundTask=None):
        response = Response(status_code=204,background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask, headers=self.Headers.build_header())
        return self._set_cookielist_to_response(response)

    def RESPONSEredirect(self, url: str, status_code: int = 307, backgroundTask=None):
        response = RedirectResponse(url=url, status_code=status_code,background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask, headers=self.Headers.build_header())
        return self._set_cookielist_to_response(response)


    def _set_cookielist_to_response(self,response):
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)