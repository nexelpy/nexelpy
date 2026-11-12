import pytest
from nexelpy import CryptoHelper
from cryptography.fernet import Fernet

def test_crypto_roundtrip_dict():
    key = Fernet.generate_key()
    crypto = CryptoHelper(key)
    
    token = crypto.encrypt(user_id=42, role="admin")
    data = crypto.decrypt(token, as_dict=True)
    
    assert data["user_id"] == 42
    assert data["role"] == "admin"

def test_crypto_roundtrip_string():
    key = Fernet.generate_key()
    crypto = CryptoHelper(key)
    
    token = crypto.encrypt("secret_data")
    data = crypto.decrypt(token)
    
    assert data == "secret_data"

def test_crypto_tampered_token():
    key = Fernet.generate_key()
    crypto = CryptoHelper(key)
    
    token = crypto.encrypt(user_id=42)
    tampered = token[:-1] + "X"
    
    assert crypto.decrypt(tampered) is None

def test_crypto_no_key_outside_request():
    # Outside of a request context, it should raise an error if no key is passed
    with pytest.raises(RuntimeError, match="could not resolve a secret key"):
        CryptoHelper()