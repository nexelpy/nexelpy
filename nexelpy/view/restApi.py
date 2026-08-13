from ..mediator.request_proxy.requestProxy import request
from ..mediator.cookiesManager import CookiesManager
from .pathBuilder import PathBuilder
import mimetypes,os
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, JSONResponse,PlainTextResponse,StreamingResponse,Response,RedirectResponse
from typing import AsyncIterable
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder

class RestApi(CookiesManager):
    def __init__(self,file=None):
        super().__init__()
        self.REQUEST = request
        self.Headers = HeaderBuilder()
        self._PathBuilder = PathBuilder(file_path=file,root=self.REQUEST._get_original_request().app.root_Path)

    
    def RESPONSEfile(self,path,type="",backgroundTask=None,disposition="attachment",):
        resolved_path = self._PathBuilder._resolve_file_path(path)
        if resolved_path is False or not resolved_path.is_file():
            return Response(status_code=404,content="File not found")

        response = FileResponse(resolved_path,status_code=200,headers=self.Headers.build_header(),
                media_type=(type if "/" in type else mimetypes.guess_type(f"file.{type}")[0]),
                background=(BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask),content_disposition_type=disposition,)
        self._setCookiesFromList(response=response)
        return response


    def RESPONSEjason(self,backgroundTask=None, **data):
        response = JSONResponse(
            content=data,
            status_code=200,
            headers=self.Headers.build_header(),
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSEtext(self, content: str, backgroundTask=None, status_code=200):
        response = PlainTextResponse(
            content=content,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSEstreaming(self,content: AsyncIterable[str | bytes], type="text/plain", backgroundTask=None, status_code=200):
        response = StreamingResponse(
            content=content,
            status_code=status_code,
            headers=self.Headers.build_header(),
            media_type= type if "/" in type else mimetypes.guess_type(f"file.{type}")[0],
            background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSEnoContent(self, backgroundTask=None):
        response = Response(status_code=204,background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask, headers=self.Headers.build_header())
        return self._setCookiesFromList(response=response)

    def RESPONSEredirect(self, url: str, status_code: int = 307, backgroundTask=None):
        response = RedirectResponse(url=url, status_code=status_code,background=BackgroundTask(backgroundTask) if callable(backgroundTask) else backgroundTask, headers=self.Headers.build_header())
        return self._setCookiesFromList(response=response)