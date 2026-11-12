import pytest
from unittest.mock import MagicMock, patch
from nexelpy.mediator.mainAppHelper.secretKey import (
    resolve_secret_key,
    CryptoHelper,
)


def test_resolve_explicit_key():
    key = b"explicit_key_value"
    assert resolve_secret_key(key) == key


def test_resolve_env_key(monkeypatch):
    monkeypatch.setenv("NEXELPY_SECRET_KEY", "env-key-value")
    assert resolve_secret_key(None) == b"env-key-value"


def test_resolve_generates_random_key(monkeypatch, capsys):
    monkeypatch.delenv("NEXELPY_SECRET_KEY", raising=False)
    key = resolve_secret_key(None)
    assert isinstance(key, bytes)
    assert len(key) == 44
    out = capsys.readouterr().out
    assert "NEXELPY_SECRET_KEY" in out


def test_crypto_with_explicit_key():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    token = c.encrypt("data")
    assert c.decrypt(token) == "data"


def test_crypto_raises_without_key():
    with pytest.raises(RuntimeError, match="could not resolve a secret key"):
        CryptoHelper()


def test_crypto_encrypt_with_data_and_kwargs():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    token = c.encrypt({"a": 1}, b=2)
    decoded = c.decrypt(token, as_dict=True)
    assert decoded == {"a": 1, "b": 2}


def test_crypto_encrypt_mixing_string_and_kwargs_raises():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    with pytest.raises(ValueError, match="Cannot mix"):
        c.encrypt("string", extra=1)


def test_crypto_encrypt_none_raises():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    with pytest.raises(ValueError, match="No data provided"):
        c.encrypt()


def test_crypto_decrypt_returns_none_on_bad_token():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    assert c.decrypt("garbage-token") is None


def test_crypto_from_request_context(tmp_path):
    from cryptography.fernet import Fernet
    from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
    from starlette.requests import Request

    key = Fernet.generate_key()
    scope = {
        "type": "http", "method": "GET", "path": "/",
        "headers": [], "query_string": b"",
        "app": MagicMock(secretKey=key),
    }
    token = set_request(Request(scope))
    try:
        c = CryptoHelper()
        token_data = c.encrypt("hello")
        assert c.decrypt(token_data) == "hello"
    finally:
        reset_request(token)


def test_crypto_encrypt_dict_roundtrip():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    c = CryptoHelper(key)
    data = {"user_id": 42, "roles": ["admin", "user"]}
    token = c.encrypt(data)
    decoded = c.decrypt(token, as_dict=True)
    assert decoded == data