import hmac
import hashlib
import secrets
import time
from ..session_proxy.sessionManager import SessionManager


class CSRFManager:
    @classmethod
    def generate_token(cls, session_data: dict) -> str:
        # 1. Create a random nonce and timestamp
        nonce = secrets.token_hex(16)
        timestamp = str(int(time.time()))
        
        # 2. Bind the token to the user's session (or empty string for guests)
        session_binding = str(session_data.get("user_id", "")) if session_data else ""
        
        # 3. Create the payload
        payload = f"{nonce}:{timestamp}:{session_binding}"
        
        # 4. Sign with HMAC using the session's secret key
        secret = SessionManager.get_fernet()._signing_key
        signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        
        return f"{payload}.{signature}"

    @classmethod
    def verify_token(cls, token: str, session_data: dict) -> bool:
        try:
            # Split payload and signature
            payload, signature = token.rsplit(".", 1)
            parts = payload.split(":")
            if len(parts) != 3:
                return False
                
            nonce, timestamp, session_binding = parts
            
            # 1. Verify the session binding (prevents token theft across sessions)
            current_binding = str(session_data.get("user_id", "")) if session_data else ""
            if not hmac.compare_digest(session_binding, current_binding):
                return False
                
            # 2. Verify the HMAC signature
            secret = SessionManager.get_fernet()._signing_key
            expected = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return False
                
            # 3. Verify the timestamp (expire tokens after 2 hours)
            if time.time() - int(timestamp) > 7200:
                return False
                
            return True
        except Exception:
            return False