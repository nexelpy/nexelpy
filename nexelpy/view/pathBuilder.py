from pathlib import Path
from posixpath import normpath


class PathBuilder:
    def __init__(self, file_path, root):
        self._project_root = Path(root).resolve()
        self._current_dir = Path(file_path).resolve().parent
        relative_dir = self._current_dir.relative_to(self._project_root)
        self._base_url = f"/{relative_dir.as_posix()}/"

    def url(self, url: str):
        if not url.startswith("."):
            return url
        dots = len(url) - len(url.lstrip("."))
        standard_url = "../" * (dots - 1) + url[dots + 1:]
        return normpath(self._base_url + standard_url)

    def _resolve_file_path(self, path: str):
        is_root_path = path.startswith("/")
        if is_root_path:
            standard_path = path[1:]
        elif path.startswith("."):
            dots = len(path) - len(path.lstrip("."))
            rest = path[dots:].lstrip("/")
            standard_path = "../" * (dots - 1) + rest
        else:
            standard_path = path

        base = self._project_root if is_root_path else self._current_dir
        resolved_path = (base / standard_path).resolve()

        try:
            resolved_path.relative_to(self._project_root)
        except ValueError:
            return Path("/")
        return resolved_path