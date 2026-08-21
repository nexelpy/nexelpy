from __future__ import annotations
from pathlib import Path
import re
from typing import Optional


URL_PATTERN = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)')


class URLResolver:
    def __init__(self,current_dir: Path,project_root: Path,):
        self.current_dir = current_dir
        self.project_root = project_root

    def url(self,relative_or_absolute_path: str,format: Optional[str] = None,) -> str:
        path = relative_or_absolute_path
        if path.startswith(("http://", "https://", "data:", "//", "/")):
            url_value = f'url("{path}")'
        else:
            target_abs_path = (self.current_dir / path).resolve()
            try:
                rel_to_root = target_abs_path.relative_to(self.project_root)
                web_path = "/" + rel_to_root.as_posix()
            except ValueError:
                web_path = ("/" + Path(path).as_posix().lstrip("/"))
            url_value = f'url("{web_path}")'
        if format is not None:
            url_value += f' format("{format}")'
        return url_value

    def resolve_raw_urls(self, raw_css: str) -> str:
        def replacer(match: re.Match) -> str:
            original_path = match.group(2).strip()
            if original_path.startswith(("http://", "https://", "data:", "//", "/")):
                return match.group(0)
            target_abs_path = (self.current_dir / original_path).resolve()
            try:
                rel_to_root = target_abs_path.relative_to(self.project_root)
                web_path = "/" + rel_to_root.as_posix()
            except ValueError:
                web_path = ("/" + Path(original_path).as_posix().lstrip("/"))
            return f'url("{web_path}")'
        return URL_PATTERN.sub(replacer, raw_css)
