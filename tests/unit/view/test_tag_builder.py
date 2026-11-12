from nexelpy.view.tagBuilder import TagBuilder

def test_tag_simple():
    tag = TagBuilder(tagName="div", text="hello")
    assert tag.build_tag == "<div>hello</div>"

def test_tag_attributes():
    tag = TagBuilder(tagName="a", text="click", href="/home", Class="link")
    assert tag.build_tag == "<a href='/home' class='link'>click</a>"

def test_tag_self_closing():
    tag = TagBuilder(tagName="img", selfClose=True, src="/logo.png")
    assert tag.build_tag == "<img src='/logo.png'/>"