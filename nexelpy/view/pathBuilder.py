from pathlib import Path
from posixpath import normpath
from functools import lru_cache

@lru_cache(maxsize=1024)
def _compute_base_paths(file_path_str: str, root_str: str):
    project_root = Path(root_str).resolve()
    current_dir = Path(file_path_str).resolve().parent
    relative_dir = current_dir.relative_to(project_root)
    base_url = f"/{relative_dir.as_posix()}/"
    return project_root, current_dir, base_url

@lru_cache(maxsize=1024)
def _cached_resolve_file(base_str: str, standard_path: str, project_root_str: str):
    resolved_path = (Path(base_str) / standard_path).resolve()
    try:
        resolved_path.relative_to(Path(project_root_str))
    except ValueError:
        return Path("/")
    return resolved_path


class PathBuilder:
    def __init__(self, file_path, root):
        file_path_str = str(file_path)
        root_str = str(root)
        self._project_root, self._current_dir, self._base_url = _compute_base_paths(file_path_str, root_str)
        self._project_root_str = str(self._project_root)

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

        base_str = self._project_root_str if is_root_path else str(self._current_dir)

        return _cached_resolve_file(base_str, standard_path, self._project_root_str)