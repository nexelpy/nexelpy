from pathlib import Path
from starlette.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse
from .static_verifier import StaticProductionVerifier

class nexelStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        StaticProductionVerifier.verify_request(scope)
        if "/static/" not in scope["path"] and not scope["path"].endswith((".js", ".css", ".html")):
            await PlainTextResponse("Not Found", status_code=404)(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


def setup_statics(app, file: str, mount_statics: bool) -> None:
    """
    Create `.nexelpy` marker and mount the static files handler.
    """
    root_dir = Path(file).resolve().parent
    (root_dir / ".nexelpy").touch(exist_ok=True)

    if mount_statics:
        app.mount("/", nexelStaticFiles(directory=root_dir), name="static")