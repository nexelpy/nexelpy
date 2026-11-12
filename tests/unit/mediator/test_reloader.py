import pytest
import time
from pathlib import Path
from nexelpy.mediator.reloader import Reloader

@pytest.fixture
def temp_project(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    
    entry_file = project_dir / "main.py"
    entry_file.write_text("print('hello')")
    
    return entry_file

def test_reloader_init(temp_project):
    reloader = Reloader(entry_file=str(temp_project))
    assert reloader.entry_file == temp_project.resolve()
    assert "__pycache__" in reloader.ignore_dirs
    assert ".py" in reloader.exts

def test_reloader_should_include(temp_project):
    reloader = Reloader(entry_file=str(temp_project))
    
    py_file = temp_project.parent / "test.py"
    txt_file = temp_project.parent / "test.txt"
    pyc_file = temp_project.parent / "__pycache__" / "test.pyc"
    
    assert reloader._should_include(py_file) is True
    assert reloader._should_include(txt_file) is False
    assert reloader._should_include(pyc_file) is False

def test_reloader_has_changes(temp_project):
    reloader = Reloader(entry_file=str(temp_project))
    
    state1 = {"a.py": 100, "b.py": 200}
    state2 = {"a.py": 100, "b.py": 200}
    state3 = {"a.py": 100, "b.py": 300}
    
    assert reloader._has_changes(state2, state1) is False
    assert reloader._has_changes(state3, state1) is True

def test_reloader_snapshot(temp_project):
    reloader = Reloader(entry_file=str(temp_project))
    
    (temp_project.parent / "test1.py").touch()
    (temp_project.parent / "test2.txt").touch()
    
    snapshot = reloader._snapshot()
    assert len(snapshot) >= 2
    assert any("test1.py" in path for path in snapshot.keys())
    assert not any("test2.txt" in path for path in snapshot.keys())

def test_reloader_ready_file(temp_project):
    reloader = Reloader(entry_file=str(temp_project))
    
    ready_file = reloader._make_ready_path()
    assert "nexelpy_ready" in ready_file.name
    assert not ready_file.exists()