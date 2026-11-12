from nexelpy.mediator.headerBuilder.headerBuilder import HeaderBuilder

def test_header_builder_strict():
    hb = HeaderBuilder()
    hb.set_strict()
    headers = hb.build_header()
    
    assert headers["X-Frame-Options"] == "SAMEORIGIN"
    assert headers["X-Content-Type-Options"] == "nosniff"

def test_header_builder_raw_override():
    hb = HeaderBuilder()
    hb.set_strict()
    hb.add_raw_header(X__Frame__Options="DENY")
    headers = hb.build_header()
    
    assert headers["X-Frame-Options"] == "DENY"