# tests/unit/mediator/test_module_inspector.py
import pytest
from nexelpy.mediator.registerations.moduleInspector import ModuleInspector


def _write(tmp_path, name, content):
    p = tmp_path / (name + ".py")
    p.write_text(content)
    return p


def test_detect_route_module(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    _write(tmp_path, "views", "from nexelpy import Route\n@Route('/x')\nasync def h(): pass\n")
    r = ModuleInspector(main, ["views"]).run()
    assert "views" in r["route_modules"]
    assert r["middleware_modules"] == []


def test_detect_middleware_module(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    _write(tmp_path, "mw", "from nexelpy import Middleware\n@Middleware(name='a')\nclass M: pass\n")
    r = ModuleInspector(main, ["mw"]).run()
    assert "mw" in r["middleware_modules"]


def test_missing_module_silently_skipped(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    r = ModuleInspector(main, ["does.not.exist"]).run()
    assert r["route_modules"] == []


def test_syntax_error_exits(tmp_path, capsys):
    main = tmp_path / "main.py"; main.write_text("")
    _write(tmp_path, "bad", "def x(:\n")
    with pytest.raises(SystemExit):
        ModuleInspector(main, ["bad"]).run()
    assert "Inspector Error" in capsys.readouterr().out


def test_extract_decorator_name_variants():
    import ast
    f = ModuleInspector._extract_decorator_name

    def get_dec(src):
        return ast.parse(src).body[0].decorator_list[0]

    assert f(get_dec("@Route\ndef h(): pass")) == "Route"
    assert f(get_dec("@Route('/x')\ndef h(): pass")) == "Route"
    assert f(get_dec("@a.b\ndef h(): pass")) == "b"
    assert f(get_dec("@a.b()\ndef h(): pass")) == "b"
    assert f(get_dec("@a.b.c\ndef h(): pass")) == "c"
    assert f(get_dec("@a.b.c()\ndef h(): pass")) == "c"