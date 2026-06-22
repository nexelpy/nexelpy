from .elementBuilder import ElementBuilder
from ..mediator.request_proxy.requestProxy import request

class FormBuilder(ElementBuilder):
    def __init__(self):
        super().__init__()
        self.REQUEST = request

    def form(self, action="#", method="post", props="", parent=None, **attributes):
        attributes["method"] = method
        attributes["action"] = action
        return self.element(tagName="form", props=props, parent=parent, **attributes)

    def input(self, props="", parent=None, **attributes):
        return self.element(tagName="input", selfClose=True, props=props, parent=parent, **attributes)

    def submit(self, text="", props="", parent=None, **attributes):
        attributes["type"] = "submit"
        attributes["value"] = f"'{text}'"
        return self.element(tagName="input", selfClose=True, props=props, parent=parent, **attributes)