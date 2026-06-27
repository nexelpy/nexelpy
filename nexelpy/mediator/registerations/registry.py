from typing import Dict, List, Any, Optional

class RouteRegistry:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._routes = []
        return cls._instance

    def register(self, route_info: Dict[str, Any]) -> None:
        self._routes.append(route_info)

    def get_all(self) -> List[Dict[str, Any]]:
        return self._routes.copy()

    def clear(self) -> None:
        self._routes.clear()

    def find_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        for item in self._routes:
            if item.get("path") == path:
                return item
        return None

    def count(self) -> int:
        return len(self._routes)

    def get_by_module(self, module_name: str) -> List[Dict[str, Any]]:
        return [item for item in self._routes if item.get("module") == module_name]