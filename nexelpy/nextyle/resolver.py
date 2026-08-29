from __future__ import annotations

import re
from typing import Optional 

URL_PATTERN = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)')


class URLResolver:
    def __init__(self, parent):
        self.parent = parent

    def resolve_raw_urls(self, raw_css: str) -> str:
        def replacer(match: re.Match) -> str:
            original_path = match.group(2).strip()
            if original_path.startswith(("http://", "https://", "data:", "//", "/")):
                return match.group(0)
            return f'url("{self.parent._url(original_path)}")'

        return URL_PATTERN.sub(replacer, raw_css)
