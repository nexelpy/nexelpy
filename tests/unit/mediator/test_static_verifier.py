import pytest
from nexelpy.mediator.mainAppHelper.static_verifier import StaticProductionVerifier


@pytest.fixture(autouse=True)
def reset_verifier_state():
    StaticProductionVerifier._warned_startup = False
    StaticProductionVerifier._warned_request = False
    yield
    StaticProductionVerifier._warned_startup = False
    StaticProductionVerifier._warned_request = False


def test_is_production_with_env_var(monkeypatch):
    monkeypatch.setenv("MAINAPP_ENV", "production")
    assert StaticProductionVerifier.is_production() is True


def test_is_production_with_hosted_hints(monkeypatch):
    monkeypatch.delenv("MAINAPP_ENV", raising=False)
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "prod")
    assert StaticProductionVerifier.is_production() is True


def test_is_local_in_dev(monkeypatch):
    monkeypatch.delenv("MAINAPP_ENV", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    assert StaticProductionVerifier.is_production() is False


def test_local_request_does_not_warn(monkeypatch, capsys):
    monkeypatch.delenv("MAINAPP_ENV", raising=False)
    scope = {"path": "/static/logo.png"}
    
    StaticProductionVerifier.verify_request(scope)
    captured = capsys.readouterr()
    
    assert "CRITICAL PRODUCTION WARNING" not in captured.out


def test_production_request_warns_when_nginx_not_configured(monkeypatch, capsys):
    monkeypatch.setenv("MAINAPP_ENV", "production")
    scope = {"path": "/static/logo.png"}
    
    StaticProductionVerifier.verify_request(scope)
    captured = capsys.readouterr()
    
    assert "CRITICAL PRODUCTION WARNING" in captured.out
    assert "Nginx is NOT configured" in captured.out


def test_production_request_does_not_warn_for_api(monkeypatch, capsys):
    monkeypatch.setenv("MAINAPP_ENV", "production")
    scope = {"path": "/api/users"}
    
    StaticProductionVerifier.verify_request(scope)
    captured = capsys.readouterr()
    
    assert "CRITICAL PRODUCTION WARNING" not in captured.out


def test_production_warning_only_printed_once(monkeypatch, capsys):
    monkeypatch.setenv("MAINAPP_ENV", "production")
    scope = {"path": "/static/style.css"}
    
    StaticProductionVerifier.verify_request(scope)
    StaticProductionVerifier.verify_request(scope)
    StaticProductionVerifier.verify_request(scope)
    
    captured = capsys.readouterr()
    assert captured.out.count("CRITICAL PRODUCTION WARNING") == 1