import base64
import hashlib
from pathlib import Path

class NexetyleNexcriptPathControl:
    def __init__(self, file: str | Path):
        self.file_path = Path(file).resolve()
        self.project_root = self._find_root()
        self.current_dir = self.file_path.parent
        self.base_url = self._get_base_url()
        self.scoping_token = self._make_scope_token()

    def _find_root(self) -> Path:
        current = self.file_path.parent

        while True:
            if (current / ".nexelpy").exists():
                return current

            if current == current.parent:
                return self.file_path.parent

            current = current.parent

    def _get_base_url(self) -> str:
        relative_dir = self.current_dir.relative_to(self.project_root)

        if relative_dir == Path("."):
            return "/"

        return f"/{relative_dir.as_posix()}"

    def _url(self, value: str) -> str:
        if not value.startswith("."):
            return value

        dots_count = len(value) - len(value.lstrip("."))
        target_suffix = value[dots_count:].lstrip("/")
        current_step = self.current_dir
        overflow_dots = 0

        for _ in range(dots_count - 1):
            if current_step == self.project_root:
                overflow_dots += 1
            else:
                current_step = current_step.parent

        rel_path = current_step.relative_to(self.project_root).as_posix()
        resolved_part = "" if rel_path == "." else f"/{rel_path}"
        suffix_part = f"/{target_suffix}" if target_suffix else ""

        if overflow_dots > 0:
            return f"{'.' * overflow_dots}{resolved_part}{suffix_part}"

        return f"{resolved_part}{suffix_part}"

    def _resolve_file_path(self, value: str | Path) -> Path:
        value = str(value).replace("\\", "/")

        if value.startswith("/"):
            return (self.project_root / value.lstrip("/")).resolve()

        if not value.startswith("."):
            return (self.current_dir / value).resolve()

        dots_count = len(value) - len(value.lstrip("."))
        target_suffix = value[dots_count:].lstrip("/")
        current_step = self.current_dir

        for _ in range(dots_count - 1):
            if current_step != self.project_root:
                current_step = current_step.parent

        return (current_step / target_suffix).resolve()

    def _make_scope_token(self) -> str:
        digest = hashlib.blake2s(
            str(self.file_path).encode("utf-8"),
            digest_size=4,
        ).digest()

        return base64.b32encode(digest).decode("ascii").lower().rstrip("=")[:5]
