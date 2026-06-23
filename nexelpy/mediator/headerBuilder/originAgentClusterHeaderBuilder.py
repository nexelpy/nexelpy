# class OriginAgentClusterHeaderBuilder:
#     header_name = "Origin-Agent-Cluster"

#     __slots__ = ("_value",)

#     def __init__(self, value: str = "?1"):
#         self._value = value

#     def build(self) -> str:
#         return self._value


class OriginAgentClusterHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self):
        self.value = "?1"

    def build_header(self):
        return {"Origin-Agent-Cluster": self.value}