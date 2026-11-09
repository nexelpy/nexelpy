from datetime import datetime
from typing import Literal
from .session_proxy.session_middleware import SessionManager
from .request_proxy.request_object import get_request


class CookiesManager:
    def __init__(self):
        super().__init__()
        self._cookies_list = []

    def set_Cookie(
        self,
        key: str,
        value: str,
        *,
        max_age: int | None = None,
        expires: datetime | str | int | None = 2678400,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
        partitioned: bool = False,
    ) -> None:
        if not key:
            raise ValueError("cookie key is required")
        self._cookies_list.append({
            "key": key,
            "value": value,
            "max_age": max_age,
            "expires": expires,
            "path": path,
            "domain": domain,
            "secure": secure,
            "httponly": httponly,
            "samesite": samesite,
            "partitioned": partitioned,
        })

    def delete_Cookie(self, *keys: str) -> None:
        if not keys:
            try:
                request = get_request()
                keys = tuple(request.cookies.keys())
            except RuntimeError:
                keys = ()
        for key in keys:
            self._cookies_list.append({
                "key": key,
                "value": "",
                "max_age": 0,
                "expires": "Thu, 01 Jan 1970 00:00:00 GMT",
                "path": "/",
                "domain": None,
                "secure": False,
                "httponly": False,
                "samesite": "lax",
                "partitioned": False,
            })

    def set_session_clientSide(
        self,
        path: str = "/",
        secure: bool | None = None,
        httponly: bool = True,
        samesite: str = "strict",
        max_age: int = 3600 * 24,
        **data,
    ) -> None:
        if secure is None:
            try:
                app = get_request().scope.get("app")
                secure = getattr(app, "session_secure", True)
            except Exception:
                secure = True

        encrypted = SessionManager.encrypt(data)
        if len(encrypted) > 3800:
            raise ValueError("session payload too large; keep session data small")
        self.set_Cookie(
            "session_clientSide",
            encrypted,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
            max_age=max_age,
        )

        # make the new session available within the same request
        try:
            request = get_request()
            request.scope.setdefault("state", {})
            request.scope["state"]["n-session"] = dict(data)
        except RuntimeError:
            pass

    def _setCookiesFromList(self, response) -> None:
        for cookie in self._cookies_list:
            params = {k: v for k, v in cookie.items() if v is not None}
            response.set_cookie(**params)
        self._cookies_list.clear()