from starlette.applications import Starlette
from .reDirect import redirect_exception_handler, RedirectException
from .mainAppHelper.static_verifier import StaticProductionVerifier
import os
import sys
import inspect
from pathlib import Path
from ..criptyle.nexcript.runtime_info import RuntimeInfo
from .reloader import Reloader
from .mainAppHelper import (
    print_branding,
    setup_routes,
    register_root_list,
    add_manual_route,
    setup_middlewares,
    setup_statics,
    run_app,
    resolve_secret_key
)


class MainAppBuilder(Starlette):
    def __init__(self, file=__file__, mountStatics=True, secretKey=None, ignore_watch_dirs=None):
        super().__init__(exception_handlers={RedirectException: redirect_exception_handler})

        # ---------- 1. core state ----------
        self.is_local = False
        self.session_secure = True
        self.file = file
        self.root_Path = os.path.dirname(os.path.abspath(file))
        self.AutoRegister_list: list[dict] = []
        self.Middleware_modules: list[str] = []
        self.manual_routes: list[dict] = []
        self.ignore_watch_dirs = ignore_watch_dirs or []
        
        # ---------- 2. Detect parent vs child  ----------
        is_direct_run = sys.argv[0].endswith(".py")
        self._is_parent = is_direct_run and not Reloader.is_child()

        # ---------- 3. Secret Key & Branding ----------
        self.secretKey = resolve_secret_key(secretKey)
        has_env_key = bool(secretKey or os.getenv("NEXELPY_SECRET_KEY"))
        
        # ---------- 4. Node.js info ----------
        info = RuntimeInfo()
        self.has_node = info.has_node
        self.node_version_ok = info.node_version_ok
        self.node_version = info.node_version

        # ---------- 5. Setup ----------
        if self._is_parent:
            print_branding(self.root_Path, self.has_node, has_secret_key=has_env_key)
        else:
            result = setup_routes(self, self.file)
            self.AutoRegister_list = result["routes"]
            self.Middleware_modules = result["middleware_modules"]
            register_root_list(self, self.AutoRegister_list)
            setup_middlewares(self)

        # ---------- 6. Production Static Files Warning ----------
        setup_statics(self, self.file, mountStatics)
        StaticProductionVerifier.verify_startup(mount_statics=mountStatics, is_direct_run=is_direct_run, is_parent=self._is_parent)
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
    def run(self, host="127.0.0.1", port=8000):
        self.is_local = True
        self.session_secure = False
        run_app(self, host=host, port=port)

    # ---------------------------------------------------------
    def add_manual_route(self, route="", prefix="", methods=None, func=None):
        return add_manual_route(self, route=route, prefix=prefix, methods=methods, func=func,)

    # ---------------------------------------------------------
    def route(self, route="", methods=["GET"], prefix=""):
        def decorator(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"Route handler '{func.__name__}' must be async (use 'async def')."
                )
            self.add_manual_route(route=route, prefix=prefix, methods=methods, func=func)
            return func
        return decorator