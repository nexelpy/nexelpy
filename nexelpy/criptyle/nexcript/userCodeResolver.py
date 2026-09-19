from __future__ import annotations

import hashlib
import posixpath
import re
from pathlib import Path
from typing import Callable, Optional


class UserCodeResolver:

    def __init__(
        self,
        code: str,
        source_file: str | Path,
        project_root: str | Path,
        scope_token: Optional[str] = None,
        import_resolver: Optional[Callable[[str, Path], str]] = None,
    ) -> None:
        self.code = code
        self.source_file = Path(source_file).resolve()
        self.project_root = Path(project_root).resolve()
        self.scope_token = scope_token or self._build_scope_token()
        self.import_resolver = import_resolver

    def _build_scope_token(self) -> str:
        value = f"{self.source_file}:{self.code}"
        digest = hashlib.sha1(value.encode()).hexdigest()[:12]
        return f"scope-{digest}"

    def resolve(self) -> str:
        code = self._resolve_scoping(self.code)
        code = self._resolve_urls(code)
        code = self._resolve_imports(code)
        return code

    def _resolve_scoping(self, code: str) -> str:
        code = self._replace_scoping_call(code)
        code = self._replace_scoping_selector(code)
        return code

    def _replace_scoping_call(self, code: str) -> str:
        replacement = f'document.querySelector("[data-scop=\\"{self.scope_token}\\"]")'
        pattern = re.compile(r"\bscoping\s*\(\s*\)")
        return self._replace_outside_strings(code, pattern, replacement)

    def _replace_scoping_selector(self, code: str) -> str:
        pattern = re.compile(
            r"\bscoping\s*\(\s*(['\"])(.*?)\1\s*\)"
        )

        def replace(match: re.Match[str]) -> str:
            selector = match.group(2).replace("\\", "\\\\").replace('"', '\\"')
            return f'document.querySelector("{selector}")'

        return self._replace_outside_strings(code, pattern, replace)

    def _resolve_urls(self, code: str) -> str:
        pattern = re.compile(
            r"\burl\s*\(\s*(['\"])([^'\"]+)\1\s*\)"
        )

        def replace(match: re.Match[str]) -> str:
            quote = match.group(1)
            value = match.group(2)

            if self._is_absolute_url(value):
                return match.group(0)

            resolved = self._resolve_asset_path(value)
            return f"url({quote}{resolved}{quote})"

        return self._replace_outside_strings(code, pattern, replace)

    def _resolve_imports(self, code: str) -> str:
        patterns = (
            re.compile(
                r"(\bimport\s+(?:[\s\S]*?\sfrom\s+)?)(['\"])([^'\"]+)(\2)"
            ),
            re.compile(
                r"(\bexport\s+(?:[\s\S]*?\sfrom\s+))(['\"])([^'\"]+)(\2)"
            ),
            re.compile(
                r"(\bimport\s*\(\s*)(['\"])([^'\"]+)(\2)(\s*\))"
            ),
        )

        for pattern in patterns:
            def replace(match: re.Match[str]) -> str:
                prefix = match.group(1)
                quote = match.group(2)
                value = match.group(3)
                suffix = match.group(4)

                resolved = self._resolve_import_path(value)

                if len(match.groups()) >= 5:
                    ending = match.group(5)
                    return f"{prefix}{quote}{resolved}{suffix}{ending}"

                return f"{prefix}{quote}{resolved}{suffix}"

            code = self._replace_outside_strings(code, pattern, replace)

        return code

    def _resolve_asset_path(self, value: str) -> str:
        value = value.replace("\\", "/")

        if value.startswith("./"):
            value = value[2:]

        source_dir = self.source_file.parent
        absolute_path = (source_dir / value).resolve()

        try:
            relative_path = absolute_path.relative_to(self.project_root)
            return relative_path.as_posix()
        except ValueError:
            return absolute_path.as_posix()

    def _resolve_import_path(self, value: str) -> str:
        if self.import_resolver:
            return self.import_resolver(value, self.source_file)

        if self._is_absolute_url(value):
            return value

        if not value.startswith("."):
            return value

        value = value.replace("\\", "/")
        source_dir = self.source_file.parent
        absolute_path = (source_dir / value).resolve()

        try:
            relative_path = absolute_path.relative_to(self.project_root)
            resolved = relative_path.as_posix()
        except ValueError:
            resolved = absolute_path.as_posix()

        if not Path(resolved).suffix:
            resolved = f"{resolved}.js"

        return resolved

    def _is_absolute_url(self, value: str) -> bool:
        return (
            value.startswith("/")
            or value.startswith("#")
            or value.startswith("data:")
            or value.startswith("http://")
            or value.startswith("https://")
            or value.startswith("//")
        )

    def _replace_outside_strings(
        self,
        code: str,
        pattern: re.Pattern[str],
        replacement: str | Callable[[re.Match[str]], str],
    ) -> str:
        result: list[str] = []
        index = 0
        length = len(code)

        while index < length:
            character = code[index]

            if character in {"'", '"', "`"}:
                end = self._find_string_end(code, index, character)
                result.append(code[index:end])
                index = end
                continue

            if code.startswith("//", index):
                end = code.find("\n", index)
                if end == -1:
                    result.append(code[index:])
                    break
                result.append(code[index:end])
                index = end
                continue

            if code.startswith("/*", index):
                end = code.find("*/", index + 2)
                if end == -1:
                    result.append(code[index:])
                    break
                end += 2
                result.append(code[index:end])
                index = end
                continue

            match = pattern.match(code, index)

            if match:
                if callable(replacement):
                    result.append(replacement(match))
                else:
                    result.append(replacement)
                index = match.end()
                continue

            result.append(character)
            index += 1

        return "".join(result)

    def _find_string_end(
        self,
        code: str,
        start: int,
        quote: str,
    ) -> int:
        index = start + 1
        length = len(code)

        while index < length:
            if code[index] == "\\":
                index += 2
                continue

            if code[index] == quote:
                return index + 1

            index += 1

        return length
