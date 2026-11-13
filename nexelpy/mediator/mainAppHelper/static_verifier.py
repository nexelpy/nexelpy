import os
from rich.console import Console

console = Console()

class StaticProductionVerifier:
    _warned_startup = False
    _warned_request = False

    @classmethod
    def is_production(cls) -> bool:
        env = (os.getenv("MAINAPP_ENV") or os.getenv("ENV") or "").lower()
        if env in ("prod", "production"):
            return True
        if any(os.getenv(k) for k in ["K_SERVICE", "DYNO", "RENDER", "RAILWAY_ENVIRONMENT"]):
            return True
        return False

    @classmethod
    def verify_startup(cls, mount_statics: bool, is_direct_run: bool, is_parent: bool):
        if not mount_statics or is_direct_run or is_parent:
            return
        if not cls.is_production():
            return

        if not cls._warned_startup:
            console.print(
                "\n[bold red]⚠ Production Static Serving Warning:[/bold red]\n"
                "   You are running a production server (e.g., uvicorn/gunicorn), but `mountStatics=True`.\n"
                "   Serving static files through Starlette is inefficient and not recommended for production.\n"
                "   [green]Recommendation:[/green] Configure Nginx to serve static files directly and set `mountStatics=False` in Nexelpy().\n"
            )
            cls._warned_startup = True

    @classmethod
    def verify_request(cls, scope):
        if not cls.is_production():
            return
        path = scope.get("path", "")
        if path.startswith("/static/") or path.endswith((".css", ".js", ".html")):
            if not cls._warned_request:
                console.print(
                    "\n[bold red]❌ CRITICAL PRODUCTION WARNING:[/bold red]\n"
                    f"   Static file requested from Starlette in PRODUCTION: [yellow]{path}[/yellow]\n"
                    "   [bold red]Nginx is NOT configured to serve static files![/bold red]\n"
                    "   Serving static files via Python in production causes severe performance issues.\n"
                    "   [green]ACTION REQUIRED:[/green] Configure Nginx to serve `/static/` and set `mountStatics=False` in Nexelpy().\n"
                )
                cls._warned_request = True