from urllib.parse import urlsplit

class CSPHeaderBuilder:
    def __init__(self):
        self.directives = {}

    @staticmethod
    def _process_source(src):
        if "'" not in src:
            u = urlsplit(src)
            if u.scheme and u.netloc:
                return f"{u.scheme}://{u.netloc}"
            return src
        return src

    def add(self, directive, *sources, origin=True):
        if directive not in self.directives:
            self.directives[directive] = []
        if origin:
            self.directives[directive].extend(map(self._process_source, sources))
        else:
            self.directives[directive].extend(sources)
        return self

    def build_header(self):
        parts = [f"{k} {' '.join(v)}".strip() for k, v in self.directives.items() if v]
        if not parts:
            return {}
        return {"Content-Security-Policy": "; ".join(parts)}