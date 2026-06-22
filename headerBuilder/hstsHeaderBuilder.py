# class HSTSHeaderBuilder:

#     header_name = "Strict-Transport-Security"

#     def __init__(self,max_age=31536000,include_subdomains=True,preload=False):
#         self.parts = [f"max-age={max_age}","includeSubDomains" if include_subdomains else "","preload" if preload else ""]

#     def build(self):
#         return "; ".join(filter(None, self.parts))


class HSTSHeaderBuilder:
    def __init__(self, max_age=31536000, include_subdomains=True, preload=False):
        
        self.max_age = max_age
        self.include_subdomains = include_subdomains or ""
        self.preload = preload or ""

    def build_header(self):
        value = f"max-age={self.max_age}"
        
        if self.include_subdomains:
            value += "; includeSubDomains"
        
        if self.preload:
            value += "; preload"
        
        return {"Strict-Transport-Security": value}