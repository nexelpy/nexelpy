import re


class ReferenceClassifier:
    def __init__(self, url_prefix: str):
        self.url_prefix = url_prefix.rstrip("/")

    def is_external(self, ref: str) -> bool:
        value = ref.strip().lower()
        return bool(
            re.match(r"^[a-z][a-z0-9+.-]*:", value)
            or value.startswith("//")
        )

    def is_canonical(self, ref: str) -> bool:
        return ref.strip().startswith(self.url_prefix + "/")

    def should_rewrite_basic(self, ref: str) -> bool:
        value = ref.strip()

        if not value:
            return False

        if self.is_external(value):
            return False

        if self.is_canonical(value):
            return False

        if value.startswith("#"):
            return False

        if value.startswith(("data:", "blob:", "mailto:", "tel:", "javascript:")):
            return False

        return True
