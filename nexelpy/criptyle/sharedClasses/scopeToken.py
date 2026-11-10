import base64
import hashlib
from pathlib import Path


def _make_scope_token(file_path: str | Path) -> str:
    """
    Generate a short, deterministic scope token from a file path.
    Used for scoping CSS and JS to prevent cross-file conflicts.
    """
    digest = hashlib.blake2s(str(file_path).encode("utf-8"), digest_size=4).digest()
    return base64.b32encode(digest).decode("ascii").lower().rstrip("=")[:5]