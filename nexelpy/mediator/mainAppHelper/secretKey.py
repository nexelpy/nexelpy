import os
import json
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
    if provided_key is not None:
        return provided_key

    env_key = os.getenv("NEXELPY_SECRET_KEY")
    if env_key:
        return env_key.encode()

    console.print(
        "[dim yellow]⚠ No NEXELPY_SECRET_KEY set. Using a random key (sessions reset on restart).[/dim yellow]"
    )
    return Fernet.generate_key()


class CryptoHelper:
    """
    A simple wrapper around Fernet to help plugin developers 
    encrypt and decrypt data safely.
    """

    def __init__(self, secret_key: bytes | None = None):
        if secret_key is None:
            try:
                from ..request_proxy.request_object import get_request
                app = get_request().scope.get("app")
                secret_key = getattr(app, "secretKey", None)
            except Exception:
                secret_key = None

        if not secret_key:
            raise RuntimeError(
                "CryptoHelper could not resolve a secret key. "
                "Make sure you are inside a request context, or pass the key explicitly."
            )

        self._fernet = Fernet(secret_key)

    def encrypt(self, data: str | dict | None = None, **kwargs) -> str:
        """
        Encrypts data into a secure token.
        Supports three modes:
        1. Keyword arguments: crypto.encrypt(user_id=42, role="admin")
        2. Dictionary: crypto.encrypt({"user_id": 42})
        3. String: crypto.encrypt("my_secret_string")
        """
        # If kwargs are provided, merge them with the data dict (or create a new one)
        if kwargs:
            if isinstance(data, dict):
                data = {**data, **kwargs}
            elif data is None:
                data = kwargs
            else:
                raise ValueError("Cannot mix a string/positional argument with keyword arguments.")

        if data is None:
            raise ValueError("No data provided to encrypt.")

        # Convert dict to JSON string
        if isinstance(data, dict):
            data = json.dumps(data)
            
        token = self._fernet.encrypt(data.encode())
        return token.decode()

    def decrypt(self, token: str, as_dict: bool = False) -> str | dict | None:
        """
        Decrypts a token back to a string or a dict.
        Returns None if the token is invalid, tampered with, or expired.
        """
        try:
            raw = self._fernet.decrypt(token.encode(), ttl=None)
            decoded = raw.decode()
            
            if as_dict:
                return json.loads(decoded)
            return decoded
            
        except Exception:
            return None