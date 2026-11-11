from ..middleware_builder import MiddlewareRegistry


def setup_middlewares(app) -> None:
    """
    Register all @Middleware classes on the Starlette app.
    Must be called AFTER routes are scanned (so MiddlewareRegistry is populated).
    """
    registry = MiddlewareRegistry()
    for middleware_class in registry.get_ordered():
        app.add_middleware(middleware_class)

    # Rebuild the middleware stack (since we added middlewares after super().__init__)
    app.middleware_stack = app.build_middleware_stack()