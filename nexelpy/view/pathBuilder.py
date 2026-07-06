from pathlib import Path
import sys
import inspect

class PathBuilder:
    def __init__(self):
        main = sys.modules.get("__main__")
        self._start = Path(main.__file__).resolve().parent if main and hasattr(main, "__file__") else Path.cwd()
        self._root = self._find_root()
        self._current_path = self._find_caller_dir()

    def _find_root(self):
        current = self._start
        while current != current.parent:
            if (current / ".nexelpy").exists():
                return current
            current = current.parent
        return None

    def _find_caller_dir(self):
        frame = inspect.currentframe()
        while frame:
            if frame.f_back is None:
                break
            frame = frame.f_back
            file_path = frame.f_globals.get("__file__")
            if file_path and "nexelpy" not in Path(file_path).resolve().parts:
                return Path(file_path).resolve().parent
        return None

    def _normalize_paths(self, attrs: dict) -> None:
        if not self._root or not self._current_path:
            return
        for key in ("src", "href"):
            value = attrs.get(key)
            if value and isinstance(value, str) and value.startswith("./"):
                full = Path(self._current_path) / value[2:]
                try:
                    rel = full.relative_to(self._root)
                    attrs[key] = "/" + str(rel).replace("\\", "/")
                except ValueError:
                    attrs[key] = str(full)

    def _resolve_file_path(self, path: str) -> str:
        if path.startswith("./"):
            base = self._current_path or self._start
            return str(Path(base) / path[2:])
        if path.startswith("/"):
            return str(Path(self._root or self._start) / path[1:])
        return path