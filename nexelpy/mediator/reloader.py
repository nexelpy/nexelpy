from __future__ import annotations

import os
import sys
import time
import subprocess

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence


# =========================================================
# runtime env
# =========================================================

@dataclass(frozen=True)
class RuntimeEnv:
    app_env: str
    is_hosted_hint: bool


def detect_runtime_env() -> RuntimeEnv:

    app_env = (
        os.getenv("MAINAPP_ENV")
        or os.getenv("ENV")
        or ""
    ).strip().lower()

    hosted_hints = any([
        bool(os.getenv("WEB_CONCURRENCY")),
        bool(os.getenv("GUNICORN_CMD_ARGS")),
        bool(os.getenv("K_SERVICE")),            # Cloud Run
        bool(os.getenv("DYNO")),                 # Heroku
        bool(os.getenv("RENDER")),               # Render
        bool(os.getenv("RAILWAY_ENVIRONMENT")), # Railway
    ])

    return RuntimeEnv(
        app_env=app_env,
        is_hosted_hint=hosted_hints,
    )


def is_production_like(env: RuntimeEnv) -> bool:
    return env.app_env in {"prod", "production"} or env.is_hosted_hint


# =========================================================
# reloader
# =========================================================

class Reloader:

    CHILD_ENV_KEY = "MAINAPP_CHILD"

    def __init__(
        self,
        entry_file: str,
        watch_dir: Optional[str] = None,
        exts: Sequence[str] = (
            ".py",
            ".html",
            ".css",
            ".js",
        ),
        ignore_dirs: Sequence[str] = (
            "__pycache__",
            ".git",
            ".idea",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
        ),
        poll_interval: float = 0.5,
        restart_on_child_exit: bool = True,
        restart_delay: float = 0.5,
        reload_cooldown: float = 1.0,
        logger=print,
    ) -> None:

        self.entry_file = Path(entry_file).resolve()

        self.watch_dir = (
            Path(watch_dir).resolve()
            if watch_dir
            else self.entry_file.parent
        )

        self.exts = tuple(e.lower() for e in exts)

        self.ignore_dirs = set(ignore_dirs)

        self.poll_interval = poll_interval
        self.restart_on_child_exit = restart_on_child_exit
        self.restart_delay = restart_delay
        self.reload_cooldown = reload_cooldown

        self.logger = logger

        self._child: Optional[subprocess.Popen] = None
        self._last_reload = 0.0

    # =====================================================
    # child checker
    # =====================================================

    @classmethod
    def is_child(cls) -> bool:
        return os.getenv(cls.CHILD_ENV_KEY) == "1"

    # =====================================================
    # file scanner
    # =====================================================

    def _iter_files(self) -> Iterable[Path]:

        for root, dirs, files in os.walk(
            self.watch_dir,
            followlinks=False,
        ):

            dirs[:] = [
                d for d in dirs
                if d not in self.ignore_dirs
            ]

            root_path = Path(root)

            for file_name in files:

                path = root_path / file_name

                if path.suffix.lower() in self.exts:
                    yield path

    # =====================================================
    # snapshot
    # =====================================================

    def _snapshot(self) -> Dict[str, float]:

        state: Dict[str, float] = {}

        for path in self._iter_files():

            try:
                state[str(path)] = path.stat().st_mtime

            except (
                FileNotFoundError,
                PermissionError,
                OSError,
            ):
                continue

        return state

    # =====================================================
    # change detector
    # =====================================================

    def _has_changes(
        self,
        current: Dict[str, float],
        previous: Dict[str, float],
    ) -> bool:

        # file added/deleted
        if set(current.keys()) != set(previous.keys()):
            return True

        # file modified
        for path, mtime in current.items():

            if previous.get(path) != mtime:
                return True

        return False

    # =====================================================
    # child process
    # =====================================================

    def _spawn_child(self) -> subprocess.Popen:

        env = os.environ.copy()

        env[self.CHILD_ENV_KEY] = "1"

        cmd = [
            sys.executable,
            str(self.entry_file),
        ]

        self.logger(
            f"[NexelPy:Reloader] nexelpy serve on http://127.0.0.1:8000 " #-> {' '.join(cmd)}"
        )

        return subprocess.Popen(
            cmd,
            env=env,
        )

    # =====================================================
    # stop child
    # =====================================================

    def _stop_child(
        self,
        timeout: float = 3.0,
    ) -> None:

        if not self._child:
            return

        if self._child.poll() is None:

            self.logger(
                "[NexelPy:Reloader] stopping child..."
            )

            self._child.terminate()

            start = time.time()

            while time.time() - start < timeout:

                if self._child.poll() is not None:
                    break

                time.sleep(0.05)

            if self._child.poll() is None:

                self.logger(
                    "[NexelPy:Reloader] force kill child"
                )

                self._child.kill()

        self._child = None

    # =====================================================
    # restart
    # =====================================================

    def _restart(
        self,
        reason: str,
    ) -> None:

        now = time.time()

        # debounce / cooldown
        if now - self._last_reload < self.reload_cooldown:
            return

        self._last_reload = now

        self.logger(
            f"[NexelPy:Reloader] {reason} -> reload"
        )

        self._stop_child()

        # allow filesystem stabilization
        time.sleep(0.2)

        self._child = self._spawn_child()

    # =====================================================
    # main loop
    # =====================================================

    def run(self) -> None:

        self.logger(
            f"[NexelPy:Reloader] watching: {self.watch_dir} "
        )

        # self.logger(
        #     f"[NexelPy:Reloader] extensions: {self.exts}"
        # )

        last_state = self._snapshot()

        self._child = self._spawn_child()

        try:

            while True:

                time.sleep(self.poll_interval)

                # -----------------------------------------
                # child crash / exit
                # -----------------------------------------

                if self._child and self._child.poll() is not None:

                    code = self._child.returncode

                    self.logger(
                        f"[NexelPy:Reloader] child exited ({code})"
                    )

                    if self.restart_on_child_exit:

                        time.sleep(self.restart_delay)

                        self._child = self._spawn_child()

                        last_state = self._snapshot()

                    continue

                # -----------------------------------------
                # detect file changes
                # -----------------------------------------

                current_state = self._snapshot()

                if self._has_changes(current_state, last_state):

                    last_state = current_state

                    self._restart("change detected")

                    # refresh snapshot after reload
                    time.sleep(0.2)

                    last_state = self._snapshot()

        except KeyboardInterrupt:

            self.logger(
                "\n[NexelPy:Reloader] stopped by user"
            )

        finally:

            self._stop_child()