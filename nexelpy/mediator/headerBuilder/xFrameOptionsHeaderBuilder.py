
class XFrameOptionsHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="DENY"):
        self.value = policy.upper()

    def build_header(self):
        return {"X-Frame-Options": self.value}