import pytest
from pathlib import Path
from nexelpy.criptyle.nexcript.code_transformer import CodeTransformer


class FakePathControl:
    def __init__(self, base="/"):
        self.scope_token = "abc12"
        self._base = base

    def url(self, value):
        if value.startswith("./"):
            return self._base + value[2:]
        return self._base + value


@pytest.fixture
def transformer():
    return lambda code: CodeTransformer(code, FakePathControl(base="/app/")).transform()


def test_scoping_empty_replaced(transformer):
    out = transformer("const el = scoping();")
    assert 'document.querySelector(\'[data-scoping="abc12"]\')' in out


def test_scoping_with_selector(transformer):
    out = transformer("const el = scoping('.card');")
    assert 'document.querySelector(\'.card\')' in out


def test_url_relative_resolved(transformer):
    out = transformer('const bg = url("./img/bg.png");')
    assert '"/app/img/bg.png"' in out


def test_url_absolute_unchanged(transformer):
    out = transformer('const x = url("/abs.png");')
    assert '"/abs.png"' in out


def test_url_http_unchanged(transformer):
    out = transformer('const x = url("https://cdn.com/a.png");')
    assert '"https://cdn.com/a.png"' in out


def test_import_relative_gets_js_extension(transformer):
    out = transformer('import { x } from "./utils";')
    assert '"/app/utils.js"' in out


def test_import_with_extension_kept(transformer):
    out = transformer('import { x } from "./utils.mjs";')
    assert '"/app/utils.mjs"' in out


def test_export_from_resolved(transformer):
    out = transformer('export { x } from "./other";')
    assert '"/app/other.js"' in out


def test_dynamic_import_resolved(transformer):
    out = transformer('const m = import("./lazy");')
    assert '"/app/lazy.js"' in out


def test_absolute_import_unchanged(transformer):
    out = transformer('import x from "/vendor/x.js";')
    assert '"/vendor/x.js"' in out


def test_bare_import_unchanged(transformer):
    out = transformer('import x from "react";')
    assert '"react"' in out


def test_line_comment_untouched(transformer):
    out = transformer('// url("./x.png") should stay\nconst y = 1;')
    assert '// url("./x.png")' in out


def test_block_comment_untouched(transformer):
    out = transformer('/* url("./x.png") */\nconst y = 1;')
    assert '/* url("./x.png") */' in out


def test_string_literal_not_transformed(transformer):
    out = transformer('const s = "hello"; const u = url("./x.png");')
    assert '"hello"' in out
    assert '"/app/x.png"' in out


def test_multiple_transforms_in_one_block(transformer):
    code = 'import { a } from "./a";\nconst b = url("./b.png");'
    out = transformer(code)
    assert '"/app/a.js"' in out
    assert '"/app/b.png"' in out


def test_comment_inside_code_preserved(transformer):
    code = 'const x = url("./a.png"); // url("./b.png") stays'
    out = transformer(code)
    assert '"/app/a.png"' in out
    assert '// url("./b.png")' in out