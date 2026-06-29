from pathlib import Path
import sys

class PathBuilder:
    def __init__(self):
        main = sys.modules.get("__main__")
        self._start = Path(main.__file__).resolve().parent if main and hasattr(main, "__file__") else Path.cwd()
        self._root = self._find_root()

    def _find_root(self):
        current = self._start
        while current != current.parent:
            if (current / ".nexelpy").exists():
                return current
            current = current.parent
        return None
    

    def _normalize_paths(self, attrs: dict) -> None:
        if not self._root:
            return
        for key in ("src", "href"):
            value = attrs.get(key)
            if value and isinstance(value, str) and value.startswith("./"):
                attrs[key] = f"/root/{value[2:]}"
            
    def _resolve_file_path(self, path: str) -> str:
        if path.startswith("./"):
            return str(Path(self._start) / path[2:])
        if path.startswith("root/"):
            if not self._root:
                raise RuntimeError("Project root missing")
            return str(Path(self._root) / path[5:])
        if path.startswith("/root/"):
            if not self._root:
                raise RuntimeError("Project root missing")
            return str(Path(self._root) / path[6:])
        return path