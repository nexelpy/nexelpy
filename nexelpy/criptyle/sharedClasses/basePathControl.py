from pathlib import Path
from ...view.pathBuilder import PathBuilder
from .scopeToken import _make_scope_token
from .projectRoot import find_project_root


class BasePathControl:
    """
    Base class for Nextyle and Nexcript.
    Handles file paths, URLs, scoping tokens, and project root detection.
    """
    def __init__(self, file: str | Path):
        self.file_path = Path(file).resolve()
        self.project_root = find_project_root(self.file_path)
        self.current_dir = self.file_path.parent
        self.scope_token = _make_scope_token(self.file_path)
        self._pathBuilder = PathBuilder(self.file_path, self.project_root)
        self.base_url = self._pathBuilder._base_url

    def url(self, value: str) -> str:
        return self._pathBuilder.url(value)

    def _resolve_file_path(self, value: str | Path) -> Path:
        return self._pathBuilder._resolve_file_path(str(value))