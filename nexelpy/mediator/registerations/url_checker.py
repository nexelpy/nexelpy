from typing import Any, Tuple


class UrlChecker:
    @staticmethod
    def check(route: Any, prefix: Any) -> Tuple[bool, str]:

        prefix = prefix or ""

        if not isinstance(route, str):
            return False, "route must be a string"

        if not isinstance(prefix, str):
            return False, "prefix must be a string"

        if not route.startswith("/"):
            return False, "route must start with '/'"

        if prefix:
            if not prefix.startswith("/"):
                return False, "prefix must start with '/'"

            if prefix.endswith("/"):
                return False, "prefix must not end with '/'"

        full_path = prefix + route

        if "//" in full_path:
            return False, "double slash detected in final url"

        return True, full_path