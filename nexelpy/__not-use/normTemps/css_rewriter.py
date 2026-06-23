import re
from pathlib import Path


class CssRewriter:
    def __init__(self, resolver, classifier):
        self.resolver = resolver
        self.classifier = classifier

        self.url_pattern = re.compile(
            r'url\(\s*(?P<quote>["\']?)(?P<ref>.*?)(?P=quote)\s*\)',
            re.IGNORECASE
        )

        self.import_pattern = re.compile(
            r'(@import\s+)(?P<quote>["\'])(?P<ref>.*?)(?P=quote)',
            re.IGNORECASE
        )

    def rewrite(self, current_file: Path, content: str) -> str:
        content = self.url_pattern.sub(lambda m: self._replace_url(current_file, m), content)
        content = self.import_pattern.sub(lambda m: self._replace_import(current_file, m), content)
        return content

    def _replace_url(self, current_file: Path, match):
        quote = match.group("quote")
        ref = match.group("ref").strip()

        if not ref or not self.classifier.should_rewrite_basic(ref):
            return match.group(0)

        rewritten = self.resolver.build(current_file, ref)
        return f"url({quote}{rewritten}{quote})"

    def _replace_import(self, current_file: Path, match):
        prefix = match.group(1)
        quote = match.group("quote")
        ref = match.group("ref").strip()

        if not ref or not self.classifier.should_rewrite_basic(ref):
            return match.group(0)

        rewritten = self.resolver.build(current_file, ref)
        return f"{prefix}{quote}{rewritten}{quote}"
