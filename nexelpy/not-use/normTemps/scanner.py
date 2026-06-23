from pathlib import Path


class TemplateScanner:
    def __init__(self, templates_root: Path):
        self.templates_root = templates_root

    def html_files(self):
        return list(self.templates_root.rglob("*.html"))

    def css_files(self):
        return list(self.templates_root.rglob("*.css"))

    def js_files(self):
        return list(self.templates_root.rglob("*.js"))
