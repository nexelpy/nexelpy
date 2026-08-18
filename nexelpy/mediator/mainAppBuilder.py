from .wraper_handler import wraper_handler
from .reloader import Reloader
from starlette.applications import Starlette
import uvicorn
from rich.console import Console
from .session_proxy.session_middleware import NexelpySessionMiddleware
from cryptography.fernet import Fernet
from.reDirect import redirect_exception_handler,RedirectException
from starlette.staticfiles import StaticFiles
from pathlib import Path
import os
from starlette.responses import PlainTextResponse
from .registerations.regestrationBuilder import RegistrationBuilder
from .session_proxy.session_middleware import SessionManager
import shutil
from typing import Any,Callable,Iterable
from .registerations.url_checker import UrlChecker

console = Console()


import logging

class UvicornAccessFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        ignored_paths = ["/.well-known/",]
        return not any(path in msg for path in ignored_paths)

class nexelStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        if "/static/" not in scope["path"]:
            response = PlainTextResponse("Not Found", status_code=404)
            await response(scope, receive, send)
            return 
        await super().__call__(scope, receive, send)



class MainAppBuilder(Starlette):
    def __init__(self, file=__file__, devMode=True,secretKey=None):
        super().__init__(exception_handlers={ RedirectException: redirect_exception_handler })
        self.file = file
        self.root_Path = os.path.dirname(os.path.abspath(file))
        self.devMode = devMode
        self.manual_routes: list[dict[str, Any]] = []

        #copy nexel-venv
        self.nexel_venv_path = Path(self.root_Path) / "nexel_venv"
        self._copy_nexel_venv()

        # session middleware
        if secretKey is None:
            secretKey = Fernet.generate_key()
        SessionManager.initialize(secretKey)
        self.add_middleware(NexelpySessionMiddleware)

        # Auto scanner
        if Reloader.is_child(): 
            self.AutoRegister_list = RegistrationBuilder(file).run()
            self._registr_root_list()
        else:
            self.auto_routes = []

        # ceate .nexelpy file for find root in page and plugins
        root_dir = Path(self.file).resolve().parent
        nexelpy_file = root_dir / ".nexelpy"
        if not nexelpy_file.exists():
            nexelpy_file.touch()

        # # mount static move to run method
        # self.mount("/", nexelStaticFiles(directory=Path(file).resolve().parent), name="static")
    #----------------------

    def _registr_root_list(self):
        if self.AutoRegister_list:
            for reg in self.AutoRegister_list:
                self.add_route(reg["path"], wraper_handler(reg["handler"]), methods=reg["method"])

    #----------------------
    def simple_run(self):
        uvicorn.run(self)
    #----------------------
    def run(self, host="127.0.0.1", port=8000):
        if self.devMode and not Reloader.is_child():
            reloader = Reloader(entry_file=self.file)
            reloader.run()
        else:
            # mount static
            self.mount("/", nexelStaticFiles(directory=Path(self.file).resolve().parent), name="static")
            #log print
            console.print(f"[bold][NexelPy MainApp][/bold] [blue]registered manual routes:[/blue] {len(self.manual_routes)}")
            console.print(f"[bold][NexelPy Registration][/bold] [green]registered routes: {len(self.AutoRegister_list)+ len(self.manual_routes) }[/green]")
            console.print("=" * 80) 

            import uvicorn
            logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())
            uvicorn.run(self, host=host, port=port)

    def _copy_nexel_venv(self):
        source = Path(__file__).resolve().parent.parent / "nexel_venv"
        if not source.exists():
            raise FileNotFoundError(source)
        if self.nexel_venv_path.exists():
            shutil.rmtree(self.nexel_venv_path)
        shutil.copytree(source, self.nexel_venv_path)

    def add_manual_route(self,route: str = "",prefix: str = "",method: str | Iterable[str] | None = None,func: Callable[..., Any] | None = None,) -> Callable[..., Any]:
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
        route_data = {"path": full_path,"method": methods,"handler": func,"module": func.__module__,"file": func.__code__.co_filename,"line": func.__code__.co_firstlineno,
            "route": route,"prefix": prefix,}
        self.manual_routes.append(route_data)
        self.add_route(full_path,wraper_handler(func),methods=methods,)
        return func
