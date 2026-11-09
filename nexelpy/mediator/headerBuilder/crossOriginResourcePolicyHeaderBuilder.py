
class CrossOriginResourcePolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="same-origin"):
        self.value = policy

    def build_header(self):
        return {"Cross-Origin-Resource-Policy": self.value}