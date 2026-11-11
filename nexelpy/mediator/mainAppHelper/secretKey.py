# nexelpy/mediator/mainAppHelper/secret_key.py
import os
from cryptography.fernet import Fernet
from rich.console import Console

console = Console()


def resolve_secret_key(provided_key: bytes | None = None) -> bytes:
    """
    Resolve the secret key from:
    1. Provided key (explicit)
    2. NEXELPY_SECRET_KEY env var
    3. Generate a random key (dev fallback)
    """
    # 1. Explicit
    if provided_key is not None:
        return provided_key

    # 2. Env var
    env_key = os.getenv("NEXELPY_SECRET_KEY")
    if env_key:
        return env_key.encode()

    # 3. Fallback: random (dev only)
    console.print(
        "[yellow][NexelPy] ⚠ No NEXELPY_SECRET_KEY set. "
        "Generated a random key. "
        "Sessions will be invalidated on every restart. "
        "For production, set NEXELPY_SECRET_KEY env var.[/yellow]"
    )
    return Fernet.generate_key()