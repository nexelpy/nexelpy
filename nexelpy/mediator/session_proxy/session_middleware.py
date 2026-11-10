from http.cookies import SimpleCookie
from .sessionManager import SessionManager


class NexelpySessionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        session_data = {}
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie")

        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header.decode())
            if "session_clientSide" in cookie:
                token = cookie["session_clientSide"].value
                session_data = SessionManager.decrypt(token)

        scope.setdefault("state", {})
        scope["state"]["session_clientSide"] = session_data

        await self.app(scope, receive, send)