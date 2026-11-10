from datetime import datetime
from typing import Literal
from .session_proxy.session_middleware import SessionManager
from .request_proxy.request_object import get_request
from .csrf.csrfManager import CSRFManager
import secrets

class CookiesManager:
    def __init__(self):
        super().__init__()
        self._cookies_list = []
        self.csrf_token = ""
        try:
            req = get_request()
            self.csrf_token = req.scope.get("state", {}).get("csrf_token", "")
        except RuntimeError:
            pass
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


    def _set_csrf_cookie_and_header(self, response) -> None:
        request = get_request()
        
        # 1. Set guest ID cookie if generated
        guest_id = request.scope.get("state", {}).get("csrf_guest_id")
        guest_key = request.scope.get("state", {}).get("csrf_guest_key")
        max_age = request.scope.get("state", {}).get("csrf_max_age", 7200)
        
        if guest_id and guest_key:
            response.set_cookie(
                key=guest_key,
                value=guest_id,
                max_age=max_age,
                path="/",
                httponly=True,
                samesite="strict",
                secure=getattr(request.scope.get("app"), "session_secure", True)
            )

        # 2. Set CSRF token (Header & Cookie)
        token = request.scope.get("state", {}).get("csrf_token", "")
        if not token:
            return

        response.headers["X-CSRF-Token"] = token
        response.set_cookie(
            key="csrf_token",
            value=token,
            max_age=max_age,
            path="/",
            httponly=True,
            samesite="strict",
            secure=getattr(request.scope.get("app"), "session_secure", True)
        )




    def set_csrf(self, max_age: int = 7200, binding_key: str = None) -> str:
        req = get_request()
        req.scope.setdefault("state", {})
        req.scope["state"]["csrf_enabled"] = True
        req.scope["state"]["csrf_max_age"] = max_age
        
        session_data = req.scope.get("state", {}).get("session_clientSide", {})
        actual_binding = binding_key
        
        # If a custom binding key is provided but doesn't exist in the session
        if binding_key is not None and binding_key not in session_data:
            # Check if we already have a guest ID in the request cookies
            guest_id = None
            for key, value in req.scope.get("headers", []):
                if key == b"cookie":
                    cookie_header = value.decode()
                    if f"{binding_key}=" in cookie_header:
                        for part in cookie_header.split(";"):
                            if part.strip().startswith(f"{binding_key}="):
                                guest_id = part.split("=")[1].strip()
                                break
                    break
            
            # If no guest ID in cookies, generate a new one
            if not guest_id:
                guest_id = secrets.token_hex(16)
                req.scope["state"]["csrf_guest_id"] = guest_id
                req.scope["state"]["csrf_guest_key"] = binding_key
            
            actual_binding = guest_id
            
        # Generate/regenerate the token
        new_token = CSRFManager.generate_token(session_data, actual_binding)
        req.scope["state"]["csrf_token"] = new_token
        req.scope["state"]["csrf_binding_key"] = actual_binding
        
        return new_token