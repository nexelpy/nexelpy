# class ClearSiteDataHeaderBuilder:
#     header_name = "Clear-Site-Data"

#     __slots__ = ("_value",)

#     def __init__(self, *directives: str):
#         if directives:
#             self._value = ", ".join(f'"{d}"' for d in directives)
#         else:
#             self._value = None

#     def build(self):
#         return self._value


class ClearSiteDataHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self, *types):
        if "*" in types:
            self.value = '"*"'
        else:
            self.value = ", ".join(f'"{t}"' for t in types)

    def build_header(self):
        return {"Clear-Site-Data": self.value}