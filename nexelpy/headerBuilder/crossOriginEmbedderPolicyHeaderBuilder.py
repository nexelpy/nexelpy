# class CrossOriginEmbedderPolicyHeaderBuilder:
#     header_name = "Cross-Origin-Embedder-Policy"

#     __slots__ = ("_value",)

#     def __init__(self, value: str = "require-corp"):
#         self._value = value

#     def build(self) -> str:
#         return self._value


class CrossOriginEmbedderPolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="require-corp"):
        self.value = policy

    def build_header(self):
        return {"Cross-Origin-Embedder-Policy": self.value}