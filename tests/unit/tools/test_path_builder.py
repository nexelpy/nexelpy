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