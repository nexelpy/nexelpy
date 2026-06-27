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
            if "n-session" in cookie:
                token = cookie["n-session"].value
                session_data = SessionManager.decrypt(token)

        scope.setdefault("state", {})
        scope["state"]["n-session"] = session_data

        await self.app(scope, receive, send)