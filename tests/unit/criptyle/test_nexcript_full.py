import pytest
from pathlib import Path
from nexelpy import Nexcript

@pytest.fixture
def project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    return tmp_path

def test_nexcript_js_generation(project_root):
    py_file = project_root / "script.py"
    py_file.touch()
    
    with Nexcript(py_file) as n:
        n.add_script("""
            function greet(name) {
                console.log("Hello, " + name);
            }
        """)
        
    js_file = project_root / "script.js"
    content = js_file.read_text()
    
    assert "function greet" in content
    assert "console.log" in content

def test_nexcript_url_resolution(project_root):
    py_file = project_root / "script.py"
    py_file.touch()
    
    with Nexcript(py_file) as n:
        n.add_script("""
            const img = url("./images/logo.png");
        """)
        
    js_file = project_root / "script.js"
    content = js_file.read_text()
    
    # The relative path should be resolved to absolute
    assert 'url("/images/logo.png")' in content or '"/images/logo.png"' in content

def test_nexcript_import_resolution(project_root):
    py_file = project_root / "script.py"
    py_file.touch()
    
    with Nexcript(py_file) as n:
        n.add_script("""
            import { helper } from "./utils";
        """)
        
    js_file = project_root / "script.js"
    content = js_file.read_text()
    
    # Should add .js extension and resolve path
    assert 'from "/utils.js"' in content or 'from "./utils.js"' in content