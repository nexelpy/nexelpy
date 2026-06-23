class MarkerService:
    def has_marker(self, content: str, marker: str) -> bool:
        return content.lstrip().startswith(marker)

    def add_marker(self, content: str, marker: str) -> str:
        if self.has_marker(content, marker):
            return content
        return f"{marker}\n{content}"
