
class OriginAgentClusterHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self):
        self.value = "?1"

    def build_header(self):
        return {"Origin-Agent-Cluster": self.value}