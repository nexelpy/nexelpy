from .wraper_handler import wraper_handler
from .reloader import Reloader, detect_runtime_env, is_production_like
from starlette.applications import Starlette
import uvicorn
from rich.console import Console
from .session_proxy.session_middleware import NexelpySessionMiddleware
from cryptography.fernet import Fernet
from .reDirect import redirect_exception_handler, RedirectException
from starlette.staticfiles import StaticFiles
from pathlib import Path
import os
import logging
from starlette.responses import PlainTextResponse
from .registerations.regestrationBuilder import RegistrationBuilder
from .session_proxy.session_middleware import SessionManager
import shutil
from typing import Any, Callable, Iterable
from .registerations.url_checker import UrlChecker
from .node_download_manager import NodeDownloadManager

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
    def __init__(self, file=__file__, devMode: bool | str = "auto",
                 mountStatics=True, secretKey=None):
        super().__init__(exception_handlers={RedirectException: redirect_exception_handler})

        # ---------- 1. devMode resolution ----------
        self.devMode = self._resolve_dev_mode(devMode)
        self.session_secure = True
        # ---------- 2. core state ----------
        self.file = file
        self.root_Path = os.path.dirname(os.path.abspath(file))
        self.AutoRegister_list: list[dict] = []
        self.manual_routes: list[dict[str, Any]] = []

        # ---------- 3. session ----------
        if secretKey is None:
            secretKey = Fernet.generate_key()
        SessionManager.initialize(secretKey)
        self.add_middleware(NexelpySessionMiddleware)

        # ---------- 4. routes (ALWAYS, in __init__) ----------
        is_dev_parent = self.devMode and not Reloader.is_child()
        if not is_dev_parent:
            self.AutoRegister_list = RegistrationBuilder(file).run()
            self._registr_root_list()

        # ---------- 5. static + .nexelpy ----------
        root_dir = Path(self.file).resolve().parent
        (root_dir / ".nexelpy").touch(exist_ok=True)
        if mountStatics:
            self.mount("/", nexelStaticFiles(directory=root_dir), name="static")

        # ---------- 6. heavy side-effects (unchanged) ----------
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
    @staticmethod
    def _resolve_dev_mode(devMode: bool | str) -> bool:
        prod = is_production_like(detect_runtime_env())
        if devMode == "auto":
            return not prod
        devMode = bool(devMode)
        if devMode and prod:
            console.print(
                "[yellow][NexelPy] devMode=True ignored: "
                "production environment detected[/yellow]"
            )
            return False
        return devMode

    # ---------------------------------------------------------
    def _registr_root_list(self):
        for reg in self.AutoRegister_list:
            self.add_route(reg["path"], wraper_handler(reg["handler"]), methods=reg["method"])

    # ---------------------------------------------------------
    def run(self, host="127.0.0.1", port=8000):
        self.session_secure = False
        self._copy_nexel_venv()
        NodeDownloadManager(__file__).ensure_node()
        # dev parent → reloader only
        if self.devMode and not Reloader.is_child():
            Reloader(entry_file=self.file).run()
            return

        console.print(f"[bold][NexelPy MainApp][/bold] [blue]registered manual routes:[/blue] {len(self.manual_routes)}")
        console.print(f"[bold][NexelPy Registration][/bold] [green]registered routes: {len(self.AutoRegister_list) + len(self.manual_routes)}[/green]")
        console.print("=" * 80)
        logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())
        uvicorn.run(self, host=host, port=port)

    # ---------------------------------------------------------
    def _copy_nexel_venv(self):
        source = Path(__file__).resolve().parent.parent / "nexel_venv"
        if not source.exists():
            raise FileNotFoundError(source)
        if self.nexel_venv_path.exists():
            import stat
            def _remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(self.nexel_venv_path, onerror=_remove_readonly)
        shutil.copytree(source, self.nexel_venv_path, symlinks=True, dirs_exist_ok=False)

    def add_manual_route(self, route: str = "", prefix: str = "",
                         method: str | Iterable[str] | None = None,
                         func: Callable[..., Any] | None = None) -> Callable[..., Any]:
        if func is None or not callable(func):
            raise TypeError("func must be a callable function")
        is_valid, full_path = UrlChecker.check(route, prefix)
        if not is_valid:
            raise ValueError(full_path)
        if method is None:
            methods = ["GET"]
        elif isinstance(method, str):
            methods = [method.upper()]
        else:
            methods = [item.upper() for item in method]
        route_data = {
            "path": full_path, "method": methods, "handler": func,
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