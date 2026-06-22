import re
from pathlib import Path


class JsRewriter:
    def __init__(self, resolver, classifier):
        self.resolver = resolver
        self.classifier = classifier

    def rewrite(self, current_file: Path, content: str) -> str:
        content = self._rewrite_static_import_from(current_file, content)
        content = self._rewrite_static_import_side_effect(current_file, content)
        content = self._rewrite_dynamic_import(current_file, content)
        content = self._rewrite_call_url_arg(current_file, content)
        content = self._rewrite_assignment(current_file, content)
        return content

    def _should_rewrite(self, ref: str) -> bool:
        value = ref.strip()

        if not self.classifier.should_rewrite_basic(value):
            return False

        if value.startswith(("./", "../", "/")):
            return True

        return self._looks_like_local_asset(value)

    def _looks_like_local_asset(self, value: str) -> bool:
        clean = value.split("?", 1)[0].split("#", 1)[0]

        if not clean:
            return False

        if clean.startswith(("{", "[", "(", "`")):
            return False

        if " " in clean:
            return False

        if "\\" in clean:
            return False

        if "/" not in clean:
            return False

        extensions = (
            ".js",
            ".mjs",
            ".json",
            ".css",
            ".html",
            ".htm",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".webp",
            ".ico",
            ".mp4",
            ".webm",
            ".mp3",
            ".wav",
            ".ogg",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".otf",
            ".txt",
            ".xml",
            ".csv"
        )

        return clean.lower().endswith(extensions)

    def _build(self, current_file: Path, ref: str) -> str:
        if not self._should_rewrite(ref):
            return ref
        return self.resolver.build(current_file, ref)

    def _rewrite_static_import_from(self, current_file: Path, content: str) -> str:
        pattern = re.compile(
            r'(\bimport\s+[\s\S]*?\s+from\s*)(["\'])([^"\']+)(\2)',
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group(1)
            quote = match.group(2)
            ref = match.group(3)
            close_quote = match.group(4)
            return f"{prefix}{quote}{self._build(current_file, ref)}{close_quote}"

        return pattern.sub(repl, content)

    def _rewrite_static_import_side_effect(self, current_file: Path, content: str) -> str:
        pattern = re.compile(
            r'(\bimport\s*)(["\'])([^"\']+)(\2)',
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group(1)
            quote = match.group(2)
            ref = match.group(3)
            close_quote = match.group(4)
            return f"{prefix}{quote}{self._build(current_file, ref)}{close_quote}"

        return pattern.sub(repl, content)

    def _rewrite_dynamic_import(self, current_file: Path, content: str) -> str:
        pattern = re.compile(
            r'(\bimport\s*\(\s*)(["\'])([^"\']+)(\2)(\s*\))',
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group(1)
            quote = match.group(2)
            ref = match.group(3)
            close_quote = match.group(4)
            suffix = match.group(5)
            return f"{prefix}{quote}{self._build(current_file, ref)}{close_quote}{suffix}"

        return pattern.sub(repl, content)

    def _rewrite_call_url_arg(self, current_file: Path, content: str) -> str:
        pattern = re.compile(
            r'(\b(?:fetch|\$\.get|\$\.post|\$\.getJSON)\s*\(\s*)(["\'])([^"\']+)(\2)',
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group(1)
            quote = match.group(2)
            ref = match.group(3)
            close_quote = match.group(4)
            return f"{prefix}{quote}{self._build(current_file, ref)}{close_quote}"

        return pattern.sub(repl, content)

    def _rewrite_assignment(self, current_file: Path, content: str) -> str:
        pattern = re.compile(
            r'(\b(?:src|href|poster|action)\s*=\s*)(["\'])([^"\']+)(\2)',
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group(1)
            quote = match.group(2)
            ref = match.group(3)
            close_quote = match.group(4)
            return f"{prefix}{quote}{self._build(current_file, ref)}{close_quote}"

        return pattern.sub(repl, content)
