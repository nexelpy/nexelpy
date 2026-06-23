from pathlib import Path


class CanonicalPathResolver:
    def __init__(self, templates_root: Path, url_prefix: str):
        self.templates_root = templates_root.resolve()
        self.url_prefix = url_prefix.rstrip("/")

    def _template_root(self, current_file: Path) -> Path:
        rel = current_file.resolve().relative_to(self.templates_root)
        return self.templates_root / rel.parts[0]

    def _split_suffix(self, ref: str):
        q = ref.find("?")
        h = ref.find("#")

        if q == -1 and h == -1:
            return ref, ""

        if q == -1:
            i = h
        elif h == -1:
            i = q
        else:
            i = min(q, h)

        return ref[:i], ref[i:]

    def build(self, current_file: Path, raw_ref: str) -> str:
        ref = raw_ref.strip()
        clean_ref, suffix = self._split_suffix(ref)

        if clean_ref.startswith("/"):
            target = self._template_root(current_file) / clean_ref.lstrip("/")
        else:
            target = (current_file.parent / clean_ref).resolve()

        rel = target.relative_to(self.templates_root)
        rel_url = "/".join(rel.parts)
        return f"{self.url_prefix}/{rel_url}{suffix}"
