from pathlib import Path

from nextyle.cssProperty import css_Property


HEADER = '''from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .nextyleBuilder import Nextyle


class KeyframeStep:
    parent: "Nextyle"
    step_name: str

    def __init__(self, parent_nextyle: "Nextyle", step_name: str) -> None: ...
    def _add_prop(self, css_prop: str, base_val: Optional[Any] = None, **kwargs: Any) -> "KeyframeStep": ...
    @staticmethod
    def _make_css_method(css_property_name: str) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
'''


def build_keyframe_step_methods() -> list[str]:
    return [
        f'    def {css_property.replace("-", "_")}(self, value: Optional[Any] = None, **kwargs: Any) -> "KeyframeStep": ...'
        for css_property in css_Property
    ]


stub_content = HEADER + "\n" + "\n".join(build_keyframe_step_methods()) + "\n"

package_dir = Path(__file__).resolve().parent
output_path = package_dir / "keyframes.pyi"
output_path.write_text(stub_content, encoding="utf-8")

print(f"KeyframeStep stub generated successfully: {output_path}")
print(f"Dynamic CSS methods: {len(css_Property)}")
