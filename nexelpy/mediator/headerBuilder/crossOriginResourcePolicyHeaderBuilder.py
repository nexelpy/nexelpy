# class CrossOriginResourcePolicyHeaderBuilder:
#     header_name = "Cross-Origin-Resource-Policy"

#     __slots__ = ("_value",)

#     def __init__(self, value: str = "same-origin"):
#         self._value = value

#     def build(self) -> str:
#         return self._value

class CrossOriginResourcePolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="same-origin"):
        self.value = policy

    def build_header(self):
        return {"Cross-Origin-Resource-Policy": self.value}