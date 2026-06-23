
from .request_proxy.request_object import set_request, reset_request
from . import _Global_nexelpy_var
from ..nexel_routes import show_erorr_in_page
import traceback
from .reDirect import RedirectException

def wraper_handler(handler):
    async def endpoint(request):

        token = set_request(request)
        try:
            return await handler()
        
        except RedirectException:
            raise
        except Exception as e:
            from datetime import datetime
            now = datetime.now().strftime("%H:%M:%S")
            tb = traceback.extract_tb(e.__traceback__)
            last = tb[-1]
            filename = last.filename
            lineno = last.lineno
            code = last.line
            
            _Global_nexelpy_var.erorr.append({"time":now,"e":e})
            return await show_erorr_in_page.show_errrr({"time":now,"e":e,"filename":filename,"line number":lineno,"code":code})

        finally:
            reset_request(token)

    return endpoint