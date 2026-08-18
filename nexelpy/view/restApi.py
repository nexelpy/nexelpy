from ..mediator.request_proxy.requestProxy import request
from ..mediator.cookiesManager import CookiesManager
from .pathBuilder import PathBuilder
import mimetypes
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, JSONResponse,PlainTextResponse,StreamingResponse,Response,RedirectResponse
from typing import AsyncIterable
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder

from typing import Any,Literal
from starlette.templating import Jinja2Templates



class RestApi(CookiesManager):
    def __init__(self, file=None):
        super().__init__()
        self.REQUEST = request
        self.Headers = HeaderBuilder()
        self._PathBuilder = PathBuilder(
            file_path=file,
            root=self.REQUEST._get_original_request().app.root_Path
        )

    def RESPONSE(
        self,
        content: str | bytes = "",
        media_type: str | None = None,
        background_task=None,
        status_code: int = 200,
    ):
        response = Response(
            content=content,
            media_type=media_type,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_json(
        self,
        background_task=None,
        status_code: int = 200,
        **data: Any,
    ):
        response = JSONResponse(
            content=data,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_text(
        self,
        text: str,
        background_task=None,
        status_code: int = 200,
    ):
        response = PlainTextResponse(
            content=text,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_streaming(
        self,
        content: AsyncIterable[str | bytes],
        media_type: str = "text/plain",
        background_task=None,
        status_code: int = 200,
    ):
        response = StreamingResponse(
            content=content,
            media_type=media_type,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_no_content(
        self,
        background_task=None,
    ):
        response = Response(
            status_code=204,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_redirect(
        self,
        url: str,
        background_task=None,
        status_code: Literal[301, 302, 303, 307, 308] = 307,
    ):
        response = RedirectResponse(
            url=url,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_file(
        self,
        path: str,
        media_type: str | None = None,
        download_name: str | None = None,
        background_task=None,
        disposition: Literal["attachment", "inline"] = "attachment",
        status_code: int = 200,
    ):
        file_path = self._PathBuilder._resolve_file_path(path)

        if file_path is False or not file_path.is_file():
            response = Response(
                content="File not found",
                status_code=404,
                headers=self.Headers.build_header(),
            )
            self._setCookiesFromList(response=response)
            return response

        response = FileResponse(
            path=file_path,
            media_type=media_type,
            filename=download_name,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
            content_disposition_type=disposition,
        )
        self._setCookiesFromList(response=response)
        return response

    def RESPONSE_html(
        self,
        html_path: str,
        background_task=None,
        status_code: int = 200,
        **data: Any,
    ):
        html = self._PathBuilder._resolve_file_path(html_path)

        if html is False or not html.is_file():
            response = Response(
                content="Template not found",
                status_code=404,
                headers=self.Headers.build_header(),
            )
            self._setCookiesFromList(response=response)
            return response

        templates = Jinja2Templates(directory=str(html.parent))

        response = templates.TemplateResponse(
            request=self.REQUEST._get_original_request(),
            name=html.name,
            context=data,
            status_code=status_code,
            headers=self.Headers.build_header(),
            background=BackgroundTask(background_task) if callable(background_task) else background_task,
        )

        self._setCookiesFromList(response=response)
        return response
