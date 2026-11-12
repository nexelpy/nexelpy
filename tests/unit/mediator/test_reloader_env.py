# tests/unit/mediator/test_reloader_env.py 

import pytest
from unittest.mock import patch
from nexelpy.mediator.reloader import detect_runtime_env, is_production_like, RuntimeEnv


def test_detect_runtime_env_reads_mainapp_env(monkeypatch):
    monkeypatch.setenv("MAINAPP_ENV", "prod")
    monkeypatch.delenv("ENV", raising=False)
    env = detect_runtime_env()
    assert env.app_env == "prod"


def test_detect_runtime_env_falls_back_to_env(monkeypatch):
    monkeypatch.delenv("MAINAPP_ENV", raising=False)
    monkeypatch.setenv("ENV", "production")
    env = detect_runtime_env()
    assert env.app_env == "production"


def test_detect_runtime_env_lowercases(monkeypatch):
    monkeypatch.setenv("MAINAPP_ENV", "PROD")
    env = detect_runtime_env()
    assert env.app_env == "prod"


def test_detect_runtime_env_detects_hosted(monkeypatch):
    monkeypatch.delenv("MAINAPP_ENV", raising=False)
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("K_SERVICE", "my-service")
    env = detect_runtime_env()
    assert env.is_hosted_hint is True


def test_detect_runtime_env_no_hints(monkeypatch):
    for k in ["MAINAPP_ENV", "ENV", "WEB_CONCURRENCY", "GUNICORN_CMD_ARGS",
              "K_SERVICE", "DYNO", "RENDER", "RAILWAY_ENVIRONMENT"]:
        monkeypatch.delenv(k, raising=False)
    env = detect_runtime_env()
    assert env.app_env == ""
    assert env.is_hosted_hint is False


@pytest.mark.parametrize("app_env,expected", [
    ("prod", True),
    ("production", True),
    ("dev", False),
    ("", False),
])
def test_is_production_like_by_env(app_env, expected):
    assert is_production_like(RuntimeEnv(app_env=app_env, is_hosted_hint=False)) is expected


def test_is_production_like_by_hosted_hint():
    assert is_production_like(RuntimeEnv(app_env="", is_hosted_hint=True)) is True