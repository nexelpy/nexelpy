from .config import NormTempsConfig
from .scanner import TemplateScanner
from .marker import MarkerService
from .classifier import ReferenceClassifier
from .path_resolver import CanonicalPathResolver
from .html_rewriter import HtmlRewriter
from .html_normalizer import HtmlNormalizer
from .css_rewriter import CssRewriter
from .css_normalizer import CssNormalizer
from .js_rewriter import JsRewriter
from .js_normalizer import JsNormalizer


class NormTemps:
    def __init__(self, config: NormTempsConfig):
        self.config = config

        self.scanner = TemplateScanner(config.templates_root)
        self.marker_service = MarkerService()
        self.classifier = ReferenceClassifier(config.url_prefix)
        self.resolver = CanonicalPathResolver(config.templates_root, config.url_prefix)

        self.html_rewriter = HtmlRewriter(self.resolver, self.classifier)
        self.css_rewriter = CssRewriter(self.resolver, self.classifier)
        self.js_rewriter = JsRewriter(self.resolver, self.classifier)

        self.html_normalizer = HtmlNormalizer(
            self.html_rewriter,
            self.marker_service,
            config.html_marker
        )

        self.css_normalizer = CssNormalizer(
            self.css_rewriter,
            self.marker_service,
            config.css_marker
        )

        self.js_normalizer = JsNormalizer(
            self.js_rewriter,
            self.marker_service,
            config.js_marker
        )

    def run(self):
        result = {
            "html": 0,
            "css": 0,
            "js": 0
        }

        for file_path in self.scanner.html_files():
            if self.html_normalizer.normalize(file_path):
                result["html"] += 1

        for file_path in self.scanner.css_files():
            if self.css_normalizer.normalize(file_path):
                result["css"] += 1

        for file_path in self.scanner.js_files():
            if self.js_normalizer.normalize(file_path):
                result["js"] += 1

        return result
