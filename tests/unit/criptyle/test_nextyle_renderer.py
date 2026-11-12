import os
from nexelpy import Nextyle
from pathlib import Path

def test_nextyle_generation(tmp_path, monkeypatch):
    # Setup a fake project root
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    
    py_file = tmp_path / "style.py"
    py_file.touch()
    
    with Nextyle(py_file) as y:
        y.select("body").color("red").padding("10px", sm="20px")
        
    css_file = tmp_path / "style.css"
    assert css_file.exists()
    
    content = css_file.read_text()
    assert "body {" in content
    assert "color: red;" in content
    assert "@media (min-width: 640px)" in content