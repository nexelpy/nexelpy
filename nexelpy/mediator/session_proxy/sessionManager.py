import json
import time
from cryptography.fernet import Fernet


class SessionManager:

    _fernet = None
    MAX_TTL = 3600 * 24 * 30  # 30 days hard cap

    @classmethod
    def initialize(cls, secret_key: bytes):
        if cls._fernet is None:
            cls._fernet = Fernet(secret_key)

    @classmethod
    def get_fernet(cls):
        if cls._fernet is None:
            raise RuntimeError("SessionManager not initialized! Call initialize() first.")
        return cls._fernet

    @classmethod
    def encrypt(cls, data: dict, max_age: int = 3600 * 24) -> str:
        max_age = min(max_age, cls.MAX_TTL)
        payload = {
            "_exp": int(time.time()) + max_age,
            "data": data,
        }
        token = cls.get_fernet().encrypt(json.dumps(payload).encode())
        return token.decode()

    @classmethod
    def decrypt(cls, token: str) -> dict:
        try:
            raw = cls.get_fernet().decrypt(token.encode(), ttl=None)
            payload = json.loads(raw)
            exp = payload.get("_exp", 0)
            if exp and time.time() > exp:
                return {}
            return payload.get("data", {})
        except Exception:
            return {}
        
    @classmethod
    def get_signing_key(cls) -> bytes:
        """Return the secret key used for HMAC signing."""
        return cls.get_fernet()._signing_key