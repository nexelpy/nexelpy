from .wraper_handler import wraper_handler
from .reloader import Reloader
from starlette.applications import Starlette
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from .session_proxy.session_middleware import NexelpySessionMiddleware
from cryptography.fernet import Fernet
from .reDirect import redirect_exception_handler, RedirectException
from starlette.staticfiles import StaticFiles
from pathlib import Path
import os
import sys
import shutil
import logging
from starlette.responses import PlainTextResponse
from .registerations.regestrationBuilder import RegistrationBuilder
from .session_proxy.session_middleware import SessionManager
from typing import Any, Callable, Iterable
from .registerations.url_checker import UrlChecker
from .csrf.csrfMiddleware import CSRFMiddleware
from .csrf.csrfManager import CSRFManager
import subprocess
from ..criptyle.nexcript.runtime_info import RuntimeInfo

console = Console()


class UvicornAccessFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not any(p in msg for p in ["/.well-known/"])


class nexelStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        if "/static/" not in scope["path"] and not scope["path"].endswith((".js", ".css", ".html")):
            await PlainTextResponse("Not Found", status_code=404)(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


class MainAppBuilder(Starlette):
    def __init__(self, file=__file__, mountStatics=True, secretKey=None, ignore_watch_dirs: list[str] | None = None):
        super().__init__(exception_handlers={RedirectException: redirect_exception_handler})

        # ---------- 1. core state ----------
        self.is_local = False 
        self.session_secure = True  
        self.file = file
        self.root_Path = os.path.dirname(os.path.abspath(file))
        self.AutoRegister_list: list[dict] = []
        self.manual_routes: list[dict[str, Any]] = []
        self.ignore_watch_dirs = ignore_watch_dirs or []

        #node
        info = RuntimeInfo()
        self.has_node = info.has_node
        self.node_version_ok = info.node_version_ok
        self.node_version = info.node_version

        # ---------- 2. Detect Parent Process ----------
        # If running via `python main.py` and not a child, we are the parent (watcher)
        is_direct_run = sys.argv[0].endswith(".py")
        self._is_parent = is_direct_run and not Reloader.is_child()

        # ---------- 3. Print Logo & Scan (Conditional) ----------
        if self._is_parent:
            # Parent only needs to print the logo. No need to scan routes!
            logo_text = Text("nexelpy", style="bold purple", justify="center")
            panel = Panel(Align.center(logo_text), border_style="purple", width=80, padding=(0, 1))
            console.print(panel)
            
            if self.has_node:
                console.print("[bold][NexelPy][/bold] [green]✓ Node.js found. (TS/JS features are available)[/green]")
            else:
                console.print("[bold][NexelPy][/bold] [yellow]⚠ Node.js not found.[/yellow] [dim]If you don't use .ts files, you can ignore this. To use NexCript, install Node.js from nodejs.org[/dim]")
            
            console.print(f"[bold][NexelPy Registration][/bold] [yellow]watching:[/yellow] {self.root_Path} [yellow]directory (Python files only)[/yellow]")
        else:
            # We are the Child process OR running in Production (uvicorn). We MUST scan.
            self.AutoRegister_list = RegistrationBuilder(file).run()
            self._registr_root_list()

        # ---------- 4. session ----------
        if secretKey is None:
            secretKey = Fernet.generate_key()
        SessionManager.initialize(secretKey)
        self.add_middleware(CSRFMiddleware)
        self.add_middleware(NexelpySessionMiddleware)
        
        # ---------- 5. static + .nexelpy ----------
        root_dir = Path(self.file).resolve().parent
        (root_dir / ".nexelpy").touch(exist_ok=True)
        if mountStatics:
            self.mount("/", nexelStaticFiles(directory=root_dir), name="static")

        # ---------- 6. heavy side-effects ----------
        self.nexel_venv_path = Path(self.root_Path) / "nexel_venv"

        # ---------- 7. signal ready to reloader ----------
        self._signal_ready()

    # ---------------------------------------------------------
    def _signal_ready(self) -> None:
        path = os.getenv("NEXELPY_READY_FILE")
        if not path:
            return
        try:
            Path(path).touch()
        except Exception:
            pass

    # ---------------------------------------------------------
    def _registr_root_list(self):
        for reg in self.AutoRegister_list:
            self.add_route(reg["path"], wraper_handler(reg["handler"]), methods=reg["methods"])

    # ---------------------------------------------------------
    def run(self, host="127.0.0.1", port=8000):
        self.is_local = True
        self.session_secure = False

        # If we are the parent process (dev mode)
        if self._is_parent:
            self._copy_nexel_venv()
            Reloader(
                entry_file=self.file,
                extra_ignore_dirs=self.ignore_watch_dirs,
            ).run()
            return

        # If we are the child process (actual server)
        console.print("=" * 80)
        console.print(f"[bold][NexelPy MainApp][/bold] [blue]registered manual routes:[/blue] {len(self.manual_routes)}")
        console.print(f"[bold][NexelPy Registration][/bold] [green]registered routes: {len(self.AutoRegister_list) + len(self.manual_routes)}[/green]")
        logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())
        uvicorn.run(self, host=host, port=port)

    # ---------------------------------------------------------
    def _copy_nexel_venv(self, force: bool = False):
        source = Path(__file__).resolve().parent.parent / "nexel_venv"
        if not source.exists():
            raise FileNotFoundError(source)

        if self.nexel_venv_path.exists():
            if not force:
                return
            import stat
            def _remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(self.nexel_venv_path, onerror=_remove_readonly)

        shutil.copytree(source, self.nexel_venv_path, symlinks=True, dirs_exist_ok=False)

    def add_manual_route(self, route: str = "", prefix: str = "",
                         methods: str | Iterable[str] | None = None,
                         func: Callable[..., Any] | None = None) -> Callable[..., Any]:
        if func is None or not callable(func):
            raise TypeError("func must be a callable function")
        is_valid, full_path = UrlChecker.check(route, prefix)
        if not is_valid:
            raise ValueError(full_path)
        if methods is None:
            methods = ["GET"]
        elif isinstance(methods, str):
            methods = [methods.upper()]
        else:
            methods = [item.upper() for item in methods]
        route_data = {
            "path": full_path, "methods": methods, "handler": func,
            "module": func.__module__, "file": func.__code__.co_filename,
            "line": func.__code__.co_firstlineno, "route": route, "prefix": prefix,
        }
        self.manual_routes.append(route_data)
        self.add_route(full_path, wraper_handler(func), methods=methods)
        for index, r in enumerate(self.routes):
            if getattr(r, "name", None) == "static":
                self.routes.append(self.routes.pop(index))
                break
        return func