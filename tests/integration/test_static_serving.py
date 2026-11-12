import os

def test_static_css_serving(app, tmp_path):
    # Create a CSS file in the project root
    # Note: The app fixture uses __file__, so we mock it to be in tmp_path
    # In a real test, we'd create a new app inside tmp_path
    from nexelpy import Nexelpy
    from starlette.testclient import TestClient
    
    main_file = tmp_path / "main.py"
    main_file.touch()
    
    css_file = tmp_path / "style.css"
    css_file.write_text("body { color: blue; }")
    
    test_app = Nexelpy(str(main_file))
    test_client = TestClient(test_app)
    
    response = test_client.get("/style.css")
    assert response.status_code == 200
    assert "color: blue;" in response.text