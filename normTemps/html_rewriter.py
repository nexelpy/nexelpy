import re
from pathlib import Path


class HtmlRewriter:
    def __init__(self, resolver, classifier):
        self.resolver = resolver
        self.classifier = classifier
        self.pattern = re.compile(
            r'(?P<attr>\b(?:href|src|poster)\b\s*=\s*)(?P<quote>["\'])(?P<ref>.*?)(?P=quote)',
            re.IGNORECASE | re.DOTALL
        )

    def rewrite(self, current_file: Path, content: str) -> str:
        def repl(match):
            attr = match.group("attr")
            quote = match.group("quote")
            ref = match.group("ref").strip()

            if not self.classifier.should_rewrite_basic(ref):
                return match.group(0)

            rewritten = self.resolver.build(current_file, ref)
            return f"{attr}{quote}{rewritten}{quote}"

        return self.pattern.sub(repl, content)
