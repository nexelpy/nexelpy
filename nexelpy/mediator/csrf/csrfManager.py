import hmac
import hashlib
import secrets
import time
from ..session_proxy.sessionManager import SessionManager


class CSRFManager:
    @classmethod
    def _get_binding(cls, session_data: dict, binding_key: str = None) -> str:
        # 1. If no key is provided, hash the entire session
        if binding_key is None:
            if not session_data:
                return ""
            sorted_items = sorted(session_data.items())
            return hashlib.sha256(str(sorted_items).encode()).hexdigest()
        
        # 2. If the key exists in the session, use its value
        if binding_key in session_data:
            return str(session_data[binding_key])
        
        # 3. If it's a random guest ID (not in session), hash it
        return hashlib.sha256(binding_key.encode()).hexdigest()

    @classmethod
    def generate_token(cls, session_data: dict, binding_key: str = None) -> str:
        nonce = secrets.token_hex(16)
        timestamp = str(int(time.time()))
        binding = cls._get_binding(session_data, binding_key)
        payload = f"{nonce}:{timestamp}:{binding}"
        
        secret = SessionManager.get_signing_key()
        signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{signature}"

    @classmethod
    def verify_token(cls, token: str, session_data: dict, binding_key: str = None, max_age: int = 7200) -> bool:
        try:
            payload, signature = token.rsplit(".", 1)
            parts = payload.split(":")
            if len(parts) != 3:
                return False
            
            nonce, timestamp, binding = parts
            current_binding = cls._get_binding(session_data, binding_key)
            
            if not hmac.compare_digest(binding, current_binding):
                return False
                
            secret = SessionManager.get_signing_key()
            expected = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return False
                
            if time.time() - int(timestamp) > max_age:
                return False
            return True
        except Exception:
            return False