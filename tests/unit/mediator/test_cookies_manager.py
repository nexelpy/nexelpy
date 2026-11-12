from nexelpy import CookiesManager

def test_set_cookie():
    cm = CookiesManager()
    cm.set_Cookie("theme", "dark", max_age=3600)
    
    assert len(cm._cookies_list) == 1
    assert cm._cookies_list[0]["key"] == "theme"
    assert cm._cookies_list[0]["value"] == "dark"

def test_delete_cookie():
    cm = CookiesManager()
    cm.delete_Cookie("theme")
    
    assert cm._cookies_list[0]["max_age"] == 0