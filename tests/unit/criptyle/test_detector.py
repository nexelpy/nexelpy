# tests/unit/criptyle/test_detector.py
import pytest
from nexelpy.criptyle.nexcript.detector import is_typescript


@pytest.mark.parametrize("code,expected", [
    # TS detection
    ("let x: number = 1;", True),
    ("const a: string = 'x';", True),
    ("function f(x: number): void {}", True),
    ("interface Foo { a: number }", True),
    ("type X = string | number;", True),
    ("const x = foo as Bar;", True),
    ("enum E { A, B }", True),
    ("import type { X } from './x';", True),
    ("export type Y = 1;", True),
    ("class A { private x = 1; }", True),
    ("const arr: number[] = [];", True),
    ("const m: Array<number> = [];", True),
    # JS — not TS
    ("function greet(name) { console.log(name); }", False),
    ("const x = 1;", False),
    ("let y = 'hello';", False),
    ("import x from './y';", False),
    ("class A { constructor() {} }", False),
    ("", False),
])
def test_detector(code, expected):
    assert is_typescript(code) is expected