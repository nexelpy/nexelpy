from contextvars import ContextVar
from starlette.requests import Request as R
from typing import Optional

_request_var: ContextVar[Optional[R]] = ContextVar("request", default=None)


def set_request(request: R):
    return _request_var.set(request)


def get_request() -> R:
    request = _request_var.get()
    if request is None:
        raise RuntimeError(
            "Request context is not initialized. "
            "Make sure the middleware is properly configured.")
    return request


def reset_request(token):
    _request_var.reset(token)