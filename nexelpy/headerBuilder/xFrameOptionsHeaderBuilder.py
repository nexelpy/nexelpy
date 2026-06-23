# class XFrameOptionsHeaderBuilder:

#     header_name = "X-Frame-Options"

#     def __init__(self, option="DENY"):
#         self._value = option

#     def build(self):
#         return self._value



class XFrameOptionsHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="DENY"):
        self.value = policy.upper()

    def build_header(self):
        return {"X-Frame-Options": self.value}