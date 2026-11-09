

class CrossOriginEmbedderPolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="require-corp"):
        self.value = policy

    def build_header(self):
        return {"Cross-Origin-Embedder-Policy": self.value}