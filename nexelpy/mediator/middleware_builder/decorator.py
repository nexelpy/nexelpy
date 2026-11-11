from __future__ import annotations
from typing import Optional
from .registry import MiddlewareRegistry


def Middleware(name: str, after: Optional[str] = None):
    """
    Register a middleware class.

    Usage:
        @Middleware(name="auth", after="session")
        class AuthMiddleware:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                ...
    """
    def decorator(cls):
        MiddlewareRegistry().register(name, cls, after)
        return cls
    return decorator