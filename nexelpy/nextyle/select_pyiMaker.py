from pathlib import Path

from nextyle.cssProperty import css_Property


PSEUDO_ITEMS = [
    "hover",
    "focus",
    "focus_visible",
    "focus_within",
    "active",
    "disabled",
    "enabled",
    "checked",
    "visited",
    "first_child",
    "last_child",
    "first_of_type",
    "last_of_type",
    "::before",
    "::after",
    "::placeholder",
    "::selection",
    "::marker",
]

HEADER = '''from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .nextyle import Nextyle


RuleKey = Tuple[str, str]


class Select:
    selector_name: str
    parent: "Nextyle"
    pseudo_suffix: str
    scope_selector: str
    rules: Dict[RuleKey, Dict[str, str]]

    def __init__(self, selector_name: str, parent_nextyle: "Nextyle", pseudo_suffix: str = "", rules: Optional[Dict[RuleKey, Dict[str, str]]] = None, scope_selector: str = "") -> None: ...
    def _add_prop(self, css_prop: str, base_val: Optional[Any] = None, **kwargs: Any) -> "Select": ...
    @staticmethod
    def _make_css_method(css_property_name: str) -> Any: ...
    @staticmethod
    def _make_pseudo_method(pseudo_target: str) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
    def pseudo(self, pseudo_name: str) -> "Select": ...
    def _render_selector(self, pseudo_suffix: str) -> str: ...
    def render_group(self, group_name: str) -> Optional[str]: ...
'''


def build_pseudo_methods() -> list[str]:
    return [f'    def {item.lstrip(":").replace("-", "_")}(self) -> "Select": ...' for item in PSEUDO_ITEMS]


def build_css_methods() -> list[str]:
    return [f'    def {css_property.replace("-", "_")}(self, value: Optional[Any] = None, **kwargs: Any) -> "Select": ...' for css_property in css_Property]


stub_content = HEADER + "\n" + "\n".join(build_pseudo_methods()) + "\n\n" + "\n".join(build_css_methods()) + "\n"

package_dir = Path(__file__).resolve().parent
output_path = package_dir / "select.pyi"
output_path.write_text(stub_content, encoding="utf-8")

print(f"Select stub generated successfully: {output_path}")
print(f"Dynamic Pseudo methods: {len(PSEUDO_ITEMS)}")
print(f"Dynamic CSS methods: {len(css_Property)}")
