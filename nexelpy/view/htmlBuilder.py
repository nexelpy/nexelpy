from .elementBuilder import ElementBuilder
from .headTagAnalyzer import HeadTagAnalyzer

class HTMLBuilder(ElementBuilder):
    def __init__(self, title="NexelPy"):
        super().__init__()
        
        self.element("!DOCTYPE html", selfClose=True, parent=self.elementsContainer)
        self.htmlTag = self.element("html", parent=self.elementsContainer)
        self.headTag = self.element("head", parent=self.htmlTag)
        self.bodyTag = self.element("body", parent=self.htmlTag)
        
        self.element("meta", parent=self.headTag, charset="UTF-8", selfClose=True)
        self.element("title", parent=self.headTag, text=title)

    def render(self) -> str:
        """Returns the raw HTML string."""
        HeadTagAnalyzer(self.headTag).analyze()
        return self.elementsContainer.content
#------ use ------
# html_builder = HTMLBuilder(title="Welcome Email")
# html_builder.h1("Hello User")
# html_string = html_builder.render() #return string
# send_email(html_string)