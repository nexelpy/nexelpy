from .wraper_handler import wraper_handler
from .reloader import Reloader, detect_runtime_env, is_production_like
from starlette.applications import Starlette
import uvicorn
from rich.console import Console
from datetime import datetime
from .session_proxy.session_middleware import NexelpySessionMiddleware
from cryptography.fernet import Fernet
from.reDirect import redirect_exception_handler,RedirectException
from starlette.staticfiles import StaticFiles
from pathlib import Path
import os
from starlette.responses import PlainTextResponse
from .registerations.regestrationBuilder import RegistrationBuilder
from .session_proxy.session_middleware import SessionManager


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

        # mount static
        self.mount("/root", nexelStaticFiles(directory=Path(file).resolve().parent), name="static")

        # session middleware
        if secretKey is None:
            secretKey = Fernet.generate_key()
        SessionManager.initialize(secretKey)
        self.add_middleware(NexelpySessionMiddleware)

        # Auto scanner
        if Reloader.is_child(): 
            self.AutoRegister_list = RegistrationBuilder(file).run()
            # console.print(f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold green](nexelpy successful find):[/bold green]")
            # console.print(f"                [blue]{len(self.AutoRegister_list)}[/blue] AutoRegister Route")
            console.print("=" * 80) 
            self._registr_root_list()
        else:
            self.auto_routes = []

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
            import uvicorn
            logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())
            uvicorn.run(self, host=host, port=port)
