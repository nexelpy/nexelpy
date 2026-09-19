import re
from pathlib import Path
from ..sharedClasses.nextyle_nexcript_path_control import NexetyleNexcriptPathControl

class CodeTransformer:
    def __init__(self, code: str, path_control: NexetyleNexcriptPathControl, scope_token: str | None = None):
        self.code = code
        self.pc = path_control
        self.scope_token = scope_token or path_control.scoping_token

    def transform(self) -> str:
        code = self._transform_scoping(self.code)
        code = self._transform_urls(code)
        code = self._transform_imports_and_exports(code)
        return code

    def _transform_scoping(self, code: str) -> str:
        pattern = r"\bscoping\s*\(\s*(?:['\"]([^'\"]*)['\"])?\s*\)"
        return self._process_non_comment_code(
            code,
            lambda segment: re.sub(
                pattern,
                lambda m: f"document.querySelector('[data-scoping=\"{self.scope_token}\"]')" if not m.group(1) else f"document.querySelector('{m.group(1).strip()}')",
                segment,
            ),
        )



    def _transform_urls(self, code: str) -> str:
        pattern = r"\burl\s*\(\s*(['\"])([^'\"]+)\1\s*\)"
        return self._process_non_comment_code(code, lambda segment: re.sub(pattern, lambda m: f"{m.group(1)}{self.pc._url(m.group(2).strip())}{m.group(1)}" if not self._is_absolute_url(m.group(2).strip()) else m.group(0), segment))

    def _transform_imports_and_exports(self, code: str) -> str:
        patterns = [
            r"(import\s+(?:(?:[\w*\s{},]*)\s+from\s+)?['\"])([^'\"]+)(['\"])",
            r"(export\s+(?:(?:[\w*\s{},]*)\s+from\s+)?['\"])([^'\"]+)(['\"])",
            r"(import\s*\(\s*['\"])([^'\"]+)(['\"]\s*\))",
        ]
        def replacer(segment: str) -> str:
            for pattern in patterns:
                segment = re.sub(pattern, lambda m: f"{m.group(1)}{self._resolve_module_specifier(m.group(2).strip())}{m.group(3)}", segment)
            return segment
        return self._process_non_comment_code(code, replacer)

    def _resolve_module_specifier(self, specifier: str) -> str:
        if self._is_absolute_url(specifier) or not specifier.startswith("."):
            return specifier
        resolved_url = self.pc._url(specifier)
        if not Path(specifier).suffix:
            return f"{resolved_url}.js"
        return resolved_url

    def _is_absolute_url(self, value: str) -> bool:
        return value.startswith(("/", "#", "data:", "http://", "https://", "//"))

    def _process_non_comment_code(self, code: str, transform_fn) -> str:
        tokens, i, n = [], 0, len(code)
        code_start = 0
        while i < n:
            if code.startswith("//", i):
                if i > code_start:
                    tokens.append(transform_fn(code[code_start:i]))
                end = code.find("\n", i)
                end = n if end == -1 else end + 1
                tokens.append(code[i:end])
                i = end
                code_start = i
            elif code.startswith("/*", i):
                if i > code_start:
                    tokens.append(transform_fn(code[code_start:i]))
                end = code.find("*/", i)
                end = n if end == -1 else end + 2
                tokens.append(code[i:end])
                i = end
                code_start = i
            else:
                i += 1
        if code_start < n:
            tokens.append(transform_fn(code[code_start:]))
        return "".join(tokens)
