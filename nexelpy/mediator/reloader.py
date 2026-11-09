from __future__ import annotations
import os
import sys
import time
import tempfile
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

DEBUG = os.getenv("NEXEL_RELOADER_DEBUG", "1") == "1"
_LOG_PATH = Path(os.getenv("NEXEL_RELOADER_LOG", "/tmp/reloader_debug.log")).resolve()


def dlog(msg: str) -> None:
    if not DEBUG:
        return
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] [pid={os.getpid()} child={os.getenv('MAINAPP_CHILD', '0')}] {msg}"
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


@dataclass(frozen=True)
class RuntimeEnv:
    app_env: str
    is_hosted_hint: bool


def detect_runtime_env() -> RuntimeEnv:
    app_env = (os.getenv("MAINAPP_ENV") or os.getenv("ENV") or "").strip().lower()
    hosted_hints = any([
        bool(os.getenv("WEB_CONCURRENCY")),
        bool(os.getenv("GUNICORN_CMD_ARGS")),
        bool(os.getenv("K_SERVICE")),
        bool(os.getenv("DYNO")),
        bool(os.getenv("RENDER")),
        bool(os.getenv("RAILWAY_ENVIRONMENT")),
    ])
    return RuntimeEnv(app_env=app_env, is_hosted_hint=hosted_hints)


def is_production_like(env: RuntimeEnv) -> bool:
    return env.app_env in {"prod", "production"} or env.is_hosted_hint


class Reloader:

    CHILD_ENV_KEY = "MAINAPP_CHILD"
    READY_ENV_KEY = "NEXELPY_READY_FILE"

    def __init__(
        self,
        entry_file: str,
        watch_dir: Optional[str] = None,
        exts: Sequence[str] = (".py",),
        ignore_dirs: Sequence[str] = (
            "__pycache__", ".git", ".idea", ".venv", "venv", "env",
            "node_modules", ".pytest_cache", ".mypy_cache",
            "nexel_venv", "dist", "build", ".tox", ".eggs",
        ),
        extra_ignore_dirs: Optional[Sequence[str]] = None,  # Added parameter for user-defined ignore dirs
        poll_interval: float = 0.4,
        restart_on_child_exit: bool = True,
        restart_delay: float = 0.5,
        reload_cooldown: float = 0.2,
        settle_window: float = 0.6,
        ready_timeout: float = 120.0,
        logger=print,
    ) -> None:
        self.entry_file = Path(entry_file).resolve()
        self.watch_dir = Path(watch_dir).resolve() if watch_dir else self.entry_file.parent
        self.exts = tuple(e.lower() for e in exts)
        
        # Merge default ignore dirs with user-provided ones
        self.ignore_dirs = set(ignore_dirs)
        if extra_ignore_dirs:
            self.ignore_dirs.update(extra_ignore_dirs)
            
        self.poll_interval = poll_interval
        self.restart_on_child_exit = restart_on_child_exit
        self.restart_delay = restart_delay
        self.reload_cooldown = reload_cooldown
        self.settle_window = settle_window
        self.ready_timeout = ready_timeout
        self.logger = logger

        self._child: Optional[subprocess.Popen] = None
        self._last_reload = time.time()
        self._pending_change_at: Optional[float] = None

        self._ready_file: Optional[Path] = None
        self._child_ready: bool = False
        self._spawn_time: float = 0.0

        dlog("=" * 70)
        dlog(f"Reloader.__init__ entry_file={self.entry_file}")
        dlog(f"Reloader.__init__ watch_dir={self.watch_dir}")
        dlog(f"Reloader.__init__ exts={self.exts}")
        dlog(f"Reloader.__init__ ignore_dirs={sorted(self.ignore_dirs)}")

    @classmethod
    def is_child(cls) -> bool:
        return os.getenv(cls.CHILD_ENV_KEY) == "1"

    def _should_include(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def _iter_files(self) -> Iterable[Path]:
        for root, dirs, files in os.walk(self.watch_dir, followlinks=False):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            root_path = Path(root)
            for file_name in files:
                path = root_path / file_name
                if "__pycache__" in path.parts:
                    continue
                if self._should_include(path):
                    yield path

    def _snapshot(self) -> Dict[str, float]:
        state: Dict[str, float] = {}
        for path in self._iter_files():
            try:
                state[str(path)] = path.stat().st_mtime
            except (FileNotFoundError, PermissionError, OSError):
                continue
        return state

    def _has_changes(self, current: Dict[str, float], previous: Dict[str, float]) -> bool:
        if set(current.keys()) != set(previous.keys()):
            return True
        for path, mtime in current.items():
            if previous.get(path) != mtime:
                return True
        return False

    def _make_ready_path(self) -> Path:
        return Path(tempfile.gettempdir()) / (
            f"nexelpy_ready_{os.getpid()}_{int(time.time() * 1000)}"
        )

    def _spawn_child(self) -> subprocess.Popen:
        self._ready_file = self._make_ready_path()
        try:
            self._ready_file.unlink(missing_ok=True)
        except Exception:
            pass

        self._child_ready = False
        self._spawn_time = time.time()

        env = os.environ.copy()
        env[self.CHILD_ENV_KEY] = "1"
        env[self.READY_ENV_KEY] = str(self._ready_file)

        cmd = [sys.executable, str(self.entry_file)]
       
        dlog(f"_spawn_child: cmd={cmd} ready_file={self._ready_file}")
        p = subprocess.Popen(cmd, env=env)
        dlog(f"_spawn_child: pid={p.pid}")
        return p

    def _stop_child(self, timeout: float = 3.0) -> None:
        if not self._child:
            return
        if self._child.poll() is None:
            self._child.terminate()
            start = time.time()
            while time.time() - start < timeout:
                if self._child.poll() is not None:
                    break
                time.sleep(0.05)
            if self._child.poll() is None:
                self.logger("[NexelPy:Reloader] force kill child")
                self._child.kill()
        self._child = None
        if self._ready_file:
            try:
                self._ready_file.unlink(missing_ok=True)
            except Exception:
                pass

    def _restart(self, reason: str) -> None:
        now = time.time()
        if now - self._last_reload < self.reload_cooldown:
            self._pending_change_at = now
            dlog("_restart DEFERRED (cooldown)")
            return
        self._last_reload = now
        dlog(f"_restart: reason='{reason}'")
        self._stop_child()
        self._child = self._spawn_child()

    def run(self) -> None:

        if DEBUG:
            console.print(f"[dim]debug log -> {_LOG_PATH}[/dim]")

        self._child = self._spawn_child()
        dlog(f"run: initial child pid={self._child.pid} — waiting for ready")

        last_state: Optional[Dict[str, float]] = None

        try:
            while True:
                time.sleep(self.poll_interval)

                if self._child and self._child.poll() is not None:
                    code = self._child.returncode
                    dlog(f"run: child exited code={code}")
                    if code != 0:
                        console.print(
                            "[bold][NexelPy Reloader][/bold] [red]server exited "
                            "and Stopping due error.[/red] "
                            "[yellow]Fix the issue and restart manually.[/yellow]"
                        )
                        break
                    else:
                        self.logger(f"[NexelPy:Reloader] child exited normally ({code})")
                        break

                if not self._child_ready:
                    ready = bool(self._ready_file and self._ready_file.exists())
                    if ready:
                        self._child_ready = True
                        last_state = self._snapshot()
                        dlog(f"run: child ready! baseline snapshot size={len(last_state)}")
                        try:
                            self._ready_file.unlink(missing_ok=True)
                        except Exception:
                            pass
                    elif time.time() - self._spawn_time > self.ready_timeout:
                        self._child_ready = True
                        last_state = self._snapshot()
                        dlog(f"run: ready TIMEOUT, snapshotting anyway (size={len(last_state)})")
                    else:
                        continue

                current_state = self._snapshot()
                if self._has_changes(current_state, last_state):
                    last_state = current_state
                    self._pending_change_at = time.time()
                    dlog("run: change detected, pending set")

                if self._pending_change_at is not None:
                    quiet = time.time() - self._pending_change_at
                    if quiet >= self.settle_window:
                        self._pending_change_at = None
                        self._restart("change detected")

        except KeyboardInterrupt:
            dlog("run: KeyboardInterrupt")
        finally:
            dlog("run: finally _stop_child")
            self._stop_child()