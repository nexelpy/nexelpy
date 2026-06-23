# class XContentTypeOptionsHeaderBuilder:

#     header_name = "X-Content-Type-Options"

#     def __init__(self, option="nosniff"):
#         self._value = option

#     def build(self):
#         return self._value



class XContentTypeOptionsHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self):
        self.value = "nosniff"

    def build_header(self):
        return {"X-Content-Type-Options": self.value}