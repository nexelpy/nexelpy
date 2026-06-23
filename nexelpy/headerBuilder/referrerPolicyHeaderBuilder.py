# class ReferrerPolicyHeaderBuilder:

#     header_name = "Referrer-Policy"

#     def __init__(self, policy="strict-origin-when-cross-origin"):
#         self._value = policy

#     def build(self):
#         return self._value


class ReferrerPolicyHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, policy="strict-origin-when-cross-origin"):
        self.value = policy

    def build_header(self):
        return {"Referrer-Policy": self.value}