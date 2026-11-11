from starlette.responses import PlainTextResponse
from .csrfManager import CSRFManager
from starlette.requests import Request
import json


class CSRFMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        scope.setdefault("state", {})
        if not scope["state"].get("csrf_clientSide_enabled", False):
            return await self.app(scope, receive, send)
        
        # 1. Ensure CSRF token exists in scope for the View to use
        session_data = scope.get("state", {}).get("session_clientSide", {})
        if "csrf_clientSide_token" not in scope.get("state", {}):
            scope.setdefault("state", {})
            # Initial default binding (None means use whole session)
            scope["state"]["csrf_clientSide_binding_key"] = None 
            scope["state"]["csrf_clientSide_token"] = CSRFManager.generate_token(session_data)
            scope["state"]["csrf_clientSide_max_age"] = 7200

        # Safe methods bypass CSRF check
        if scope["method"] in ("GET", "HEAD", "OPTIONS"):
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        token = headers.get(b"x-csrf-clientside", b"").decode()

        # 2. If no header, extract from Form Body safely
        if not token:
            content_type = headers.get(b"content-type", b"").decode()
            
            if "application/x-www-form-urlencoded" in content_type:
                body = b""
                more_body = True
                while more_body:
                    message = await receive()
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)
                
                scope["cached_body"] = body
                
                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}

                from urllib.parse import parse_qs
                try:
                    form_data = parse_qs(body.decode())
                    token = form_data.get("csrf_clientSide_token", [""])[0]
                except Exception:
                    pass
            
            elif "application/json" in content_type:
                body = b""
                more_body = True
                while more_body:
                    message = await receive()
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)
                scope["cached_body"] = body
                
                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}
                try:
                    json_data = json.loads(body.decode())
                    token = json_data.get("csrf_token", "")
                except Exception:
                    pass

        # 3. Verify token
        if not token:
            response = PlainTextResponse("CSRF token missing", status_code=403)
            await response(scope, receive, send)
            return

        max_age = scope.get("state", {}).get("csrf_max_age", 7200)
        binding_key = scope.get("state", {}).get("csrf_binding_key", None)
        
        if not CSRFManager.verify_token(token, session_data, binding_key=binding_key, max_age=max_age):
            response = PlainTextResponse("CSRF token invalid or expired", status_code=403)
            await response(scope, receive, send)
            return

        # Token is valid, proceed to the View
        await self.app(scope, receive, send)