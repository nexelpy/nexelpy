
class XContentTypeOptionsHeaderBuilder:
    __slots__ = ['value']
    
    def __init__(self):
        self.value = "nosniff"

    def build_header(self):
        return {"X-Content-Type-Options": self.value}