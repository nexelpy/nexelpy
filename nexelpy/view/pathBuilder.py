from pathlib import Path
from posixpath import normpath
import os

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
        dots = len(path) - len(path.lstrip("."))
        standard_path = (path[1:] if is_root_path else "../" * (dots - 1) + path[dots + 1:])
        resolved_path = (self._project_root if is_root_path else self._current_dir) / standard_path
        resolved_path = resolved_path.resolve()

        project_root_str = str(self._project_root)
        resolved_path_str = str(resolved_path)
        if not resolved_path_str.startswith(project_root_str + os.sep) and resolved_path_str != project_root_str:
            return Path("/")  # Return "/" invalid paths
        return resolved_path