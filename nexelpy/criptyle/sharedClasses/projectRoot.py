from pathlib import Path


def find_project_root(file_path: str | Path) -> Path:
    """
    Walk up from file_path until we find a .nexelpy marker.
    Fallback: return the file's parent directory.
    """
    file_path = Path(file_path).resolve()
    current = file_path.parent
    while True:
        if (current / ".nexelpy").exists():
            return current
        if current == current.parent:
            return file_path.parent
        current = current.parent