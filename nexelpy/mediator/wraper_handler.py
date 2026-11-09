import logging
import traceback
from datetime import datetime

from .request_proxy.request_object import set_request, reset_request
from .show_error_in_view import show_error_in_view
from .reDirect import RedirectException

logger = logging.getLogger("nexelpy.handler")


def _find_user_frame(tb):
    frames = traceback.extract_tb(tb)
    user_frames = [f for f in frames if "nexelpy" not in f.filename]
    return user_frames[-1] if user_frames else (frames[-1] if frames else None)


def wraper_handler(handler):
    async def endpoint(request):
        token = set_request(request)
        try:
            return await handler()
        except RedirectException:
            raise
        except Exception as e:
            mainapp = request.scope.get("app")
            is_local = getattr(mainapp, "is_local", False)

            # In production, log the full traceback to console
            if not is_local:
                logger.exception("Unhandled exception in handler")

            # In local/dev, show the beautiful graphical error page
            if is_local:
                now = datetime.now().strftime("%H:%M:%S")
                frame = _find_user_frame(e.__traceback__)
                info = {
                    "Time": now,
                    "Error": e,
                    "Module path": getattr(frame, "filename", "?"),
                    "Line number": getattr(frame, "lineno", "?"),
                    "Code": getattr(frame, "line", "?"),
                }
                try:
                    return await show_error_in_view(info, file=mainapp.file)
                except Exception:
                    logger.exception("Failed to render error view")

            raise
        finally:
            reset_request(token)

    return endpoint