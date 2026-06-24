import json
from http.cookies import SimpleCookie
from cryptography.fernet import InvalidToken
from .. import _Global_nexelpy_var as g


class NexelpySessionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        session_data = {}

        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie")

        if cookie_header and g.FERNET:
            cookie = SimpleCookie()
            cookie.load(cookie_header.decode())

            if "n-session" in cookie:
                token = cookie["n-session"].value
                try:
                    decrypted = g.FERNET.decrypt(token.encode()).decode()
                    session_data = json.loads(decrypted)
                except (InvalidToken, json.JSONDecodeError):
                    session_data = {}
        scope.setdefault("state", {})
        scope["state"]["n-session"] = session_data

        await self.app(scope, receive, send)
