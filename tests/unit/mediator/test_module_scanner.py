# tests/unit/mediator/test_module_scanner.py
import pytest
from nexelpy.mediator.registerations.moduleScanner import ModuleScanner


def _project(tmp_path):
    (tmp_path / ".nexelpy").touch()
    main = tmp_path / "main.py"
    main.write_text("")
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").touch()
    (pkg / "views.py").touch()
    (tmp_path / "top.py").touch()
    # noise
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "x.py").touch()
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "should_not.py").touch()
    return main


def test_scan_lists_modules(tmp_path):
    main = _project(tmp_path)
    mods = ModuleScanner(main).run()
    assert "pkg.views" in mods
    assert "top" in mods
    # main.py excluded
    assert "main" not in mods


def test_scan_skips_pycache_and_venv(tmp_path):
    main = _project(tmp_path)
    mods = ModuleScanner(main).run()
    assert all("__pycache__" not in m for m in mods)
    assert all("should_not" not in m for m in mods)


def test_init_file_maps_to_package_name(tmp_path):
    main = _project(tmp_path)
    mods = ModuleScanner(main).run()
    assert "pkg" in mods


def test_missing_file_exits(capsys):
    with pytest.raises(SystemExit):
        ModuleScanner(None).run()
    assert "root_progect is not set" in capsys.readouterr().out