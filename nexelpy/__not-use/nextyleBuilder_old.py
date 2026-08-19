from pathlib import Path
import re
from typing import Dict, List, Any, Optional, Tuple

URL_PATTERN = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)')

# (media_group, pseudo_suffix) -> CSS properties
# Examples:
# ("base", "")
# ("sm", "")
# ("base", ":hover")
# ("lg", ":hover")
RuleKey = Tuple[str, str]


class Select:
    def __init__(
        self,
        selector_name: str,
        parent_nextyle: "Nextyle",
        pseudo_suffix: str = "",
        rules: Optional[Dict[RuleKey, Dict[str, str]]] = None,
    ):
        self.selector_name = selector_name
        self.parent = parent_nextyle
        self.pseudo_suffix = pseudo_suffix

        # pseudo viewها باید ruleهای selector اصلی را share کنند.
        # وگرنه چون فقط selector اصلی در _actions ثبت شده، ruleهای hover رندر نمی‌شوند.
        self.rules: Dict[RuleKey, Dict[str, str]] = (
            rules if rules is not None else {}
        )

    def _add_prop(
        self,
        css_prop: str,
        base_val: Optional[str] = None,
        **kwargs,
    ):
        """
        Example:
            .background_color("blue", sm="red")

        Base selector:
            ("base", "") -> { "background-color": "blue" }

        Hover selector:
            ("sm", ":hover") -> { "background-color": "red" }
        """
        if base_val is not None:
            self.rules.setdefault(
                ("base", self.pseudo_suffix),
                {},
            )[css_prop] = str(base_val)

        for bp_key, val in kwargs.items():
            if bp_key not in self.parent.media_queries:
                available = ", ".join(self.parent.media_queries.keys())
                raise KeyError(
                    f"Unknown media query key: '{bp_key}'. "
                    f"Available keys: {available}"
                )

            if val is not None:
                self.rules.setdefault(
                    (bp_key, self.pseudo_suffix),
                    {},
                )[css_prop] = str(val)

        return self

    @staticmethod
    def _make_css_method(css_property_name: str):
        def method(self: "Select", value: Optional[str] = None, **kwargs):
            return self._add_prop(css_property_name, value, **kwargs)

        method.__name__ = css_property_name.replace("-", "_")
        method.__doc__ = f"Set CSS '{css_property_name}' property."
        return method

    def pseudo(self, pseudo_name: str) -> "Select":
        """
        یک pseudo-class یا pseudo-element به selector فعلی اضافه می‌کند.

        Examples:
            .pseudo("hover")             -> .btn:hover
            .pseudo(":focus-visible")    -> .btn:focus-visible
            .pseudo("has(.icon)")        -> .btn:has(.icon)
            .pseudo("nth-child(odd)")    -> .btn:nth-child(odd)
            .pseudo("::before")          -> .btn::before

        همچنین امکان ترکیب وجود دارد:
            .hover().focus()
            -> .btn:hover:focus
        """
        pseudo_name = pseudo_name.strip()

        if not pseudo_name:
            raise ValueError("Pseudo name cannot be empty.")

        if not pseudo_name.startswith(":"):
            pseudo_name = f":{pseudo_name}"

        return Select(
            selector_name=self.selector_name,
            parent_nextyle=self.parent,
            pseudo_suffix=f"{self.pseudo_suffix}{pseudo_name}",
            rules=self.rules,
        )

    # ---------- Common pseudo-class shortcuts ----------

    def hover(self) -> "Select":
        return self.pseudo("hover")

    def focus(self) -> "Select":
        return self.pseudo("focus")

    def focus_visible(self) -> "Select":
        return self.pseudo("focus-visible")

    def focus_within(self) -> "Select":
        return self.pseudo("focus-within")

    def active(self) -> "Select":
        return self.pseudo("active")

    def disabled(self) -> "Select":
        return self.pseudo("disabled")

    def enabled(self) -> "Select":
        return self.pseudo("enabled")

    def checked(self) -> "Select":
        return self.pseudo("checked")

    def visited(self) -> "Select":
        return self.pseudo("visited")

    def first_child(self) -> "Select":
        return self.pseudo("first-child")

    def last_child(self) -> "Select":
        return self.pseudo("last-child")

    def first_of_type(self) -> "Select":
        return self.pseudo("first-of-type")

    def last_of_type(self) -> "Select":
        return self.pseudo("last-of-type")

    # ---------- Common pseudo-element shortcuts ----------

    def before(self) -> "Select":
        return self.pseudo("::before")

    def after(self) -> "Select":
        return self.pseudo("::after")

    def placeholder(self) -> "Select":
        return self.pseudo("::placeholder")

    def selection(self) -> "Select":
        return self.pseudo("::selection")

    def marker(self) -> "Select":
        return self.pseudo("::marker")

    def render_group(self, group_name: str) -> Optional[str]:
        """
        تمام selectorهای این action را برای یک group مشخص رندر می‌کند.

        Examples:
            render_group("base")
            render_group("sm")
            render_group("lg")
        """
        rendered_blocks: List[str] = []

        for (rule_group, pseudo_suffix), properties in self.rules.items():
            if rule_group != group_name or not properties:
                continue

            lines = [f"{self.selector_name}{pseudo_suffix} {{"]

            for prop, val in properties.items():
                lines.append(f"    {prop}: {val};")

            lines.append("}")
            rendered_blocks.append("\n".join(lines))

        return "\n\n".join(rendered_blocks) if rendered_blocks else None


from .cssProperty import css_Property as CSS_PROPERTIES

for prop in CSS_PROPERTIES:
    method_name = prop.replace("-", "_")
    setattr(Select, method_name, Select._make_css_method(prop))


class Nextyle:
    DEFAULT_MEDIA_QUERIES = {
        "sm": "@media (min-width: 640px)",
        "md": "@media (min-width: 768px)",
        "lg": "@media (min-width: 1024px)",
        "xl": "@media (min-width: 1280px)",
        "ul": "@media (min-width: 1536px)",
    }

    def __init__(
        self,
        file: str,
        export_path: Optional[str] = None,
        **custom_media_queries,
    ):
        self.file_path = Path(file).resolve()
        self.current_dir = self.file_path.parent
        self.project_root = self._find_project_root(self.file_path)

        if export_path:
            target = Path(export_path)

            if target.is_absolute():
                self.export_file = target
            else:
                self.export_file = (self.current_dir / target).resolve()
        else:
            self.export_file = self.file_path.with_suffix(".css")

        self.media_queries = self.DEFAULT_MEDIA_QUERIES.copy()
        self.media_queries.update(custom_media_queries)

        self._actions: List[Any] = []

    def _find_project_root(self, start_file: Path) -> Path:
        current = start_file.parent

        for parent in [current, *current.parents]:
            if (parent / ".nexelpy").exists():
                return parent

        return current

    def url(self, relative_or_absolute_path: str) -> str:
        if relative_or_absolute_path.startswith(
            ("http://", "https://", "data:", "//", "/")
        ):
            return f'url("{relative_or_absolute_path}")'

        target_abs_path = (
            self.current_dir / relative_or_absolute_path
        ).resolve()

        try:
            rel_to_root = target_abs_path.relative_to(self.project_root)
            web_path = "/" + rel_to_root.as_posix()
        except ValueError:
            web_path = "/" + Path(relative_or_absolute_path).as_posix().lstrip("/")

        return f'url("{web_path}")'

    def _resolve_raw_urls(self, raw_css: str) -> str:
        def replacer(match: re.Match) -> str:
            original_path = match.group(2).strip()

            if original_path.startswith(
                ("http://", "https://", "data:", "//", "/")
            ):
                return match.group(0)

            target_abs_path = (self.current_dir / original_path).resolve()

            try:
                rel_to_root = target_abs_path.relative_to(self.project_root)
                web_path = "/" + rel_to_root.as_posix()
            except ValueError:
                web_path = "/" + Path(original_path).as_posix().lstrip("/")

            return f'url("{web_path}")'

        return URL_PATTERN.sub(replacer, raw_css)

    def select(self, selector_name: str) -> Select:
        sel = Select(selector_name, self)
        self._actions.append(sel)
        return sel

    def add_raw_css(self, raw_css: Optional[str] = None, **kwargs):
        if raw_css is not None:
            resolved = self._resolve_raw_urls(raw_css.strip())
            self._actions.append(("raw", "base", resolved))

        for bp_key, content in kwargs.items():
            if bp_key not in self.media_queries:
                available = ", ".join(self.media_queries.keys())
                raise KeyError(
                    f"Unknown media query key: '{bp_key}'. "
                    f"Available keys: {available}"
                )

            resolved = self._resolve_raw_urls(content.strip())
            self._actions.append(("raw", bp_key, resolved))

    def generate_css(self) -> str:
        final_sections: List[str] = []

        # ---------- Base rules ----------
        base_blocks: List[str] = []

        for action in self._actions:
            if isinstance(action, Select):
                rendered = action.render_group("base")

                if rendered:
                    base_blocks.append(rendered)

            elif (
                isinstance(action, tuple)
                and action[0] == "raw"
                and action[1] == "base"
            ):
                base_blocks.append(action[2])

        if base_blocks:
            final_sections.append("\n\n".join(base_blocks))

        # ---------- Merged media-query blocks ----------
        for bp_key, media_rule in self.media_queries.items():
            media_blocks: List[str] = []

            for action in self._actions:
                if isinstance(action, Select):
                    rendered = action.render_group(bp_key)

                    if rendered:
                        media_blocks.append(rendered)

                elif (
                    isinstance(action, tuple)
                    and action[0] == "raw"
                    and action[1] == bp_key
                ):
                    media_blocks.append(action[2])

            if media_blocks:
                inner_css = "\n\n".join(media_blocks)

                indented_inner = "\n".join(
                    f"    {line}" if line.strip() else ""
                    for line in inner_css.splitlines()
                )

                final_sections.append(
                    f"{media_rule} {{\n"
                    f"{indented_inner}\n"
                    f"}}"
                )

        return "\n\n".join(final_sections) + "\n"

    def export(self):
        css_content = self.generate_css()
        self.export_file.parent.mkdir(parents=True, exist_ok=True)
        self.export_file.write_text(css_content, encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.export()