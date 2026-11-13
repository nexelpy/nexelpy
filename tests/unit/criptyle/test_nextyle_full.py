import pytest
from pathlib import Path
from nexelpy import Nextyle

@pytest.fixture
def project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    return tmp_path

def test_nextyle_media_queries(project_root):
    py_file = project_root / "style.py"
    py_file.touch()
    
    with Nextyle(py_file) as y:
        y.select(".card").padding("4px", sm="8px", md="12px", lg="20px", ul="24px")
        
    css_file = project_root / "style.css"
    content = css_file.read_text()
    
    assert ".card {" in content
    assert "padding: 4px;" in content
    assert "@media (min-width: 576px)" in content
    assert "padding: 8px;" in content
    assert "@media (min-width: 768px)" in content
    assert "padding: 12px;" in content
    assert "@media (min-width: 992px)" in content
    assert "padding: 20px;" in content

def test_nextyle_keyframes(project_root):
    py_file = project_root / "style.py"
    py_file.touch()
    
    with Nextyle(py_file) as y:
        with y.keyframes("fade-in"):
            y.step("0%").opacity("0")
            y.step("100%").opacity("1")
            
    css_file = project_root / "style.css"
    content = css_file.read_text()
    
    assert "@keyframes fade-in" in content
    assert "0% {" in content
    assert "opacity: 0;" in content
    assert "100% {" in content
    assert "opacity: 1;" in content

def test_nextyle_scoping(project_root):
    py_file = project_root / "style.py"
    py_file.touch()
    
    with Nextyle(py_file) as y:
        with y.scoping():
            y.select("p").color("red")
            
    css_file = project_root / "style.css"
    content = css_file.read_text()
    
    # Should generate a scoped selector with a random token
    assert "[data-scoping=" in content
    assert "p {" in content
    assert "color: red;" in content

def test_nextyle_font_face(project_root):
    py_file = project_root / "style.py"
    py_file.touch()
    
    with Nextyle(py_file) as y:
        with y.font_face("MyFont"):
            y.src(y.url("./font.woff2", format="woff2"))
            y.font_weight("400")
            
    css_file = project_root / "style.css"
    content = css_file.read_text()
    
    assert "@font-face {" in content
    assert 'font-family: "MyFont";' in content
    assert "font-weight: 400;" in content