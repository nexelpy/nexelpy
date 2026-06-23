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
        self.directives[directive].extend(map(self._process_source, sources))  if origin else self.directives[directive].extend(sources)
        return self

    def build_header(self):
        return {"Content-Security-Policy": '; '.join(f"{key} {' '.join(values)}" for key, values in self.directives.items() if values)} if self.directives else {}

# # استفاده
# csp = CSPHeaderBuilder()
# csp.add('default-src', "'self'", "'unsafe-inline'")
# csp.add('default-src', "https://viiiiiiiiiiiiiiiiii")
# csp.add('script-src', "'self'", "https://example.com", "http://test.com")
# csp.add('style-src', "'self'", "https://cdn.com")

# headers = csp.build_header()
# print(headers)
