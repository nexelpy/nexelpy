from __future__ import annotations

import re


class URLResolver:
    RAW_URL_PATTERN = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)')

    def __init__(self, parent):
        self.parent = parent

    def resolve(self, value: str) -> str:
        if value.startswith(("http://", "https://", "data:", "//", "/")):
            return value
        return self.parent._url(value)

    def resolve_raw_css(self, raw_css: str) -> str:
        def replacer(match: re.Match[str]) -> str:
            original_path = match.group(2).strip()
            resolved_path = self.resolve(original_path)
            return f'url("{resolved_path}")'

        return self.RAW_URL_PATTERN.sub(replacer, raw_css)
