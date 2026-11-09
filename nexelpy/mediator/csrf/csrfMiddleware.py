from starlette.responses import PlainTextResponse
from urllib.parse import parse_qs
from .csrfManager import CSRFManager


class CSRFMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # NexelPy only supports GET and POST. Safe methods bypass CSRF.
        if scope["method"] in ("GET", "HEAD", "OPTIONS"):
            return await self.app(scope, receive, send)

        session_data = scope.get("state", {}).get("session_clientSide", {})
        headers = dict(scope.get("headers", []))
        
        # 1. Try to get token from Header (AJAX / JSON)
        token = headers.get(b"x-csrf-token", b"").decode()
        
        # 2. If no header, try to get from Form Body (Traditional HTML Forms)
        if not token:
            content_type = headers.get(b"content-type", b"").decode()
            if "application/x-www-form-urlencoded" in content_type:
                body = b""
                more_body = True
                while more_body:
                    message = await receive()
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)
                
                # Parse form data
                try:
                    form_data = parse_qs(body.decode())
                    token = form_data.get("csrf_token", [""])[0]
                except Exception:
                    pass
                
                # Re-inject the body so the actual View handler can read it
                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}

        # 3. Verify token existence and validity
        if not token:
            return PlainTextResponse("CSRF token missing", status_code=403)

        if not CSRFManager.verify_token(token, session_data):
            return PlainTextResponse("CSRF token invalid or expired", status_code=403)

        # Token is valid, proceed to the View
        await self.app(scope, receive, send)