from pathlib import Path


class CssNormalizer:
    def __init__(self, rewriter, marker_service, marker: str):
        self.rewriter = rewriter
        self.marker_service = marker_service
        self.marker = marker

    def normalize(self, file_path: Path) -> bool:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        if self.marker_service.has_marker(content, self.marker):
            return False

        rewritten = self.rewriter.rewrite(file_path, content)
        rewritten = self.marker_service.add_marker(rewritten, self.marker)

        file_path.write_text(rewritten, encoding="utf-8")
        return rewritten != content
