from starlette.responses import RedirectResponse


class RedirectException(Exception):
    def __init__(self, url: str, status_code: int = 307):
        super().__init__(url, status_code)
        self.url = url
        self.status_code = status_code


async def redirect_exception_handler(request, exc: RedirectException):
    return RedirectResponse(url=exc.url, status_code=exc.status_code)


def redirect_now(url: str, status_code: int = 307):
    raise RedirectException(url, status_code)
