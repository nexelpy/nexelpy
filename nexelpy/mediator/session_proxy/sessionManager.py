import json
from cryptography.fernet import Fernet


class SessionManager:

    _fernet = None

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
    def encrypt(cls, data: dict) -> str:
        json_data = json.dumps(data)
        encrypted = cls.get_fernet().encrypt(json_data.encode())
        return encrypted.decode()

    @classmethod
    def decrypt(cls, token: str) -> dict:
        try:
            decrypted = cls.get_fernet().decrypt(token.encode())
            return json.loads(decrypted)
        except Exception:
            return {}