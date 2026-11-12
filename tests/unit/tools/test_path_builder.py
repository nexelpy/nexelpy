import pytest
from pathlib import Path
from nexelpy.view.pathBuilder import PathBuilder

def test_path_relative(tmp_path):
    project_root = tmp_path
    current_dir = project_root / "views"
    current_dir.mkdir()
    file_path = current_dir / "main.py"
    file_path.touch()
    
    pb = PathBuilder(file_path, project_root)
    
    # Test URL generation
    assert pb.url("./style.css") == "/views/style.css"
    
    # Test file resolution
    resolved = pb._resolve_file_path("./style.css")
    assert resolved == current_dir / "style.css"

def test_path_security_traversal(tmp_path):
    project_root = tmp_path
    file_path = project_root / "main.py"
    file_path.touch()
    
    pb = PathBuilder(file_path, project_root)
    
    # Attempt to access outside of project root
    result = pb._resolve_file_path("../../etc/passwd")
    
    # It should return "/" (invalid path)
    assert result == Path("/")



def test_plain_relative_without_dot(tmp_path):
    (tmp_path / "hello.txt").write_text("x")
    pb = PathBuilder(tmp_path / "main.py", tmp_path)
    assert pb._resolve_file_path("hello.txt") == tmp_path / "hello.txt"


def test_dot_relative_unchanged(tmp_path):
    (tmp_path / "f.txt").write_text("x")
    pb = PathBuilder(tmp_path / "main.py", tmp_path)
    assert pb._resolve_file_path("./f.txt") == tmp_path / "f.txt"


def test_dotdot_up_one_level(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "f.txt").write_text("x")
    pb = PathBuilder(sub / "main.py", tmp_path)
    assert pb._resolve_file_path("../f.txt") == tmp_path / "f.txt"


def test_dotdot_escapes_project_root_blocked(tmp_path):
    pb = PathBuilder(tmp_path / "main.py", tmp_path)
    assert pb._resolve_file_path("../outside.txt") == Path("/")

