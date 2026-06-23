from .formBuilder import FormBuilder
from .importerExporter import Importer
from ..mediator.reDirect import redirect_now
from urllib.parse import urlencode
from .setCookieSession import SetCookieSession
from ..mediator.headerBuilder.headerBuilder import HeaderBuilder

class PluginBuilder(Importer,SetCookieSession,FormBuilder): 
    def __init__(self):
        super().__init__()
        self.Headers = HeaderBuilder()

    def redirect(self, url: str, status_code: int = 307, **kwargs):
        if kwargs:
            params = {key: value for key, value in kwargs.items() if value is not None}
            if params:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{urlencode(params, doseq=False)}"
        redirect_now(url=url, status_code=status_code)

    def RESPONSE(self,*arg):
        self._plugin_return_func_data = arg
        return self