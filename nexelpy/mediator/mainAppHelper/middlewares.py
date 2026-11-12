# nexelpy/mediator/mainAppHelper/middlewares.py
from ..middleware_builder import MiddlewareRegistry


def setup_middlewares(app) -> None:
    registry = MiddlewareRegistry()
    for middleware_class in reversed(registry.get_ordered()):
        app.add_middleware(middleware_class)
    app.middleware_stack = app.build_middleware_stack()