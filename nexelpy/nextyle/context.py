from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .nextyleBuilder import Nextyle


class CSSContext:
    def __init__(
        self,
        parent: "Nextyle",
        context_type: str,
        value: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.parent = parent
        self.context_type = context_type
        self.value = value
        self.extra = extra or {}

        # ترتیب عملیات داخل context
        self.actions: List[Any] = []

        # برای @font-face، @property، @page و vars
        self.declarations: Dict[str, str] = {}

        # برای @keyframes
        #
        # {
        #     "from": {"opacity": "0"},
        #     "to": {"opacity": "1"},
        # }
        self.keyframe_rules: Dict[
            str,
            Dict[str, str],
        ] = {}


class ContextManager:
    def __init__(
        self,
        nextyle: "Nextyle",
        context_type: str,
        value: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.nextyle = nextyle
        self.context_type = context_type
        self.value = value
        self.extra = extra

    def __enter__(self):
        self.nextyle._push_context(
            context_type=self.context_type,
            value=self.value,
            extra=self.extra,
        )

        return self.nextyle

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.nextyle._pop_context()
        return False


class FontFaceContextManager:
    def __init__(
        self,
        nextyle: "Nextyle",
        family_name: str,
    ):
        self.nextyle = nextyle
        self.family_name = family_name

    def __enter__(self):
        context = self.nextyle._push_context(
            context_type="font-face",
        )

        context.declarations["font-family"] = (
            f'"{self.family_name}"'
        )

        return self.nextyle

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.nextyle._pop_context()
        return False
