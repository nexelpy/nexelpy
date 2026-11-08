class ClearSiteDataHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, *types):
        if "*" in types:
            self.value = '"*"'
        else:
            self.value = ", ".join(f'"{t}"' for t in types)

    def build_header(self):
        if not self.value:
            return {}
        return {"Clear-Site-Data": self.value}