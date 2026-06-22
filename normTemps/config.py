from dataclasses import dataclass
from pathlib import Path


@dataclass
class NormTempsConfig:
    templates_root: Path
    url_prefix: str = "/root/templates"
    html_marker: str = "<!-- normTemps:normalized:html:v2 -->"
    css_marker: str = "/* normTemps:normalized:css:v2 */"
    js_marker: str = "/* normTemps:normalized:js:v1 */"

    def __post_init__(self):
        self.templates_root = Path(self.templates_root).resolve()
        self.url_prefix = self.url_prefix.rstrip("/")
