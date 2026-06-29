import sys
import os
from urllib.parse import urlsplit
from functools import lru_cache
from ..mediator import _Global_nexelpy_var


class PathBuilder:
    def __init__(self):
        super().__init__()
        self._instance_directory = self._get_caller_dir()
        self._project_root = _Global_nexelpy_var.project_root_dir

        if self._project_root:
            self._project_root_len = len(self._project_root) + 1

    def _get_caller_dir(self):
        frame = sys._getframe(2)
        while frame:
            file_path = frame.f_globals.get("__file__")
            if file_path and "nexelpy" not in (norm := os.path.abspath(file_path)):
                return os.path.dirname(norm)
            frame = frame.f_back
        return None

    @lru_cache(512)
    def _path_generate(self, path: str) -> str | None:

        if path.startswith("./"):
            if not (self._instance_directory and self._project_root):
                raise RuntimeError("Context (dir/root) missing")

            abs_path = os.path.join(self._instance_directory, path[2:])

            if abs_path.startswith(self._project_root):
                rel = abs_path[self._project_root_len:]
            else:
                rel = os.path.relpath(abs_path, self._project_root)

            rel_url = rel.replace(os.sep, "/")


            if "/static/" not in f"/{rel_url}/":
                return None

            return "/root/" + rel_url

        if path.startswith("root/"):
            rel_url = path[5:]

            if "/static/" not in f"/{rel_url}/":
                return None

            return "/" + path
        
        return path

    def _resolve_file_path(self, path: str) -> str:
        if path.startswith("./"):
            if not self._instance_directory: raise RuntimeError("Instance dir missing")
            return os.path.join(self._instance_directory, path[2:])
            
        if path.startswith("root/"):
            if not self._project_root: raise RuntimeError("Project root missing")
            return os.path.join(self._project_root, path[5:])
        return path