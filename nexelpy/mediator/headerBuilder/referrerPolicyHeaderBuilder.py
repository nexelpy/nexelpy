
class ReferrerPolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="strict-origin-when-cross-origin"):
        self.value = policy

    def build_header(self):
        return {"Referrer-Policy": self.value}