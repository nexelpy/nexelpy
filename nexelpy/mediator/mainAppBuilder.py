from . import _Global_nexelpy_var
from .registerations.moduleScanner import ModuleScanner
from .registerations.moduleInspector import ModuleInspector
from .registerations.moduleRunHasDecorator import ModuleRunHasDecorator
from .wraper_handler import wraper_handler
from .reloader import Reloader, detect_runtime_env, is_production_like
from starlette.applications import Starlette
import uvicorn,sys
from rich.console import Console
from datetime import datetime
from .session_proxy.session_middleware import NexelpySessionMiddleware
from cryptography.fernet import Fernet
from.reDirect import redirect_exception_handler,RedirectException
from starlette.staticfiles import StaticFiles
from pathlib import Path
import os
from starlette.responses import PlainTextResponse


class MyStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        if "/static/" not in scope["path"]:
            response = PlainTextResponse("Not Found", status_code=404)
            await response(scope, receive, send)
            return
        await super().__call__(scope, receive, send)



class MainAppBuilder:
    def __init__(self,file=__file__,devMode=True):
        
        if _Global_nexelpy_var.root_progect is not None:   #-----check nexelpy not run in other prosses without venve
            print("nexelpy run in another project, try with venv.")
        else:
            _Global_nexelpy_var.root_progect = file
            self.root_dir = os.path.dirname(os.path.abspath(file))
            _Global_nexelpy_var.project_root_dir = self.root_dir
            _Global_nexelpy_var.dev_Mode = devMode
            #---------------- make starlette app --------------------
            self.app = Starlette(exception_handlers={ RedirectException: redirect_exception_handler })
            _Global_nexelpy_var.__starlette__ = self.app
            #-----------------mount static file ----
            self.app.mount("/root",MyStaticFiles(directory=Path(file).resolve().parent),name="static")
            #-----------------session middleware---------
            fernet_key = Fernet.generate_key()     
            _Global_nexelpy_var.FERNET = Fernet(fernet_key)
            self.app.add_middleware(NexelpySessionMiddleware)
            #-----------------Auto scanner-------------
            ModuleScanner().run()
            ModuleInspector.run()
            ModuleRunHasDecorator.run()
            console = Console()
            console.print(f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold green](nexelpy successful find):[/bold green]")
            console.print(f"                [blue]{len(_Global_nexelpy_var.AutoRegister_list)}[/blue] AutoRegister Route")
            console.print(f"                [blue]{len(_Global_nexelpy_var.manualRegister_list)}[/blue] manualRegister Route")
            self._registr_root_list()

    #----------------------
    def _registr_root_list(self):
        if _Global_nexelpy_var.AutoRegister_list:
            for reg in _Global_nexelpy_var.AutoRegister_list:
                self.app.add_route(reg["path"], wraper_handler(reg["handler"]), methods=reg["method"])
    #----------------------
    def run(self,host="127.0.0.1",port=8000,):
        env = detect_runtime_env()

        if is_production_like(env):
            uvicorn.run(self.app,host=host,port=port,access_log=False,log_level="warning")
            return

        if Reloader.is_child():
            uvicorn.run(self.app,host=host,port=port,access_log=False,log_level="warning")
            return

        entry_file = sys.modules["__main__"].__file__
        reloader = Reloader(entry_file=entry_file)
        reloader.run()

    def simple_run(self):
        uvicorn.run(self.app)