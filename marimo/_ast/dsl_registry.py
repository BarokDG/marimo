# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from marimo._ast.dsl import CellDSL
    from marimo._ast.visitor import ScopedVisitor

FindDefsAndRefs = Callable[["ScopedVisitor", ast.Call, str], None]


@dataclass(frozen=True)
class _DSLCallHandler:
    """What `ScopedVisitor.visit_Call` dispatches on for a registered DSL."""

    language: str
    find_defs_and_refs: FindDefsAndRefs | None


class _CellDSLRegistry:
    """Registry of custom (non-SQL) DSL cell detectors.

    SQL is intentionally never registered here -- it keeps its own
    hand-written detection in `ScopedVisitor.visit_Call`, untouched. This
    registry only holds DSLs registered via `register_cell_dsl`.
    """

    def __init__(self) -> None:
        self._by_call_name: dict[str, _DSLCallHandler] = {}
        self._call_names_by_language: dict[str, tuple[str, ...]] = {}

    def register_detector(
        self,
        *,
        language: str,
        call_names: tuple[str, ...],
        find_defs_and_refs: FindDefsAndRefs | None = None,
    ) -> None:
        handler = _DSLCallHandler(language, find_defs_and_refs)
        for call_name in call_names:
            self._by_call_name[call_name] = handler
        self._call_names_by_language[language] = call_names

    def get(self, call_name: str) -> _DSLCallHandler | None:
        return self._by_call_name.get(call_name)

    def registered_dsls(self) -> dict[str, tuple[str, ...]]:
        """Currently registered DSL names, mapped to their call names."""
        return dict(self._call_names_by_language)


CELL_DSL_REGISTRY = _CellDSLRegistry()


def register_cell_dsl(dsl: CellDSL) -> None:
    """Register a `CellDSL` so marimo recognizes and runs `mo.<name>(...)`.

    This installs `mo.<name>` as a callable and registers the DSL's call
    names for cell-language detection and (optional) cross-cell ref/def
    extraction.
    """
    import marimo
    from marimo._ast.dsl import CellDSL as _CellDSL
    from marimo._messaging.notification import DSLRegisteredNotification
    from marimo._messaging.notification_utils import broadcast_notification

    find_defs_and_refs = (
        dsl.find_defs_and_refs
        if type(dsl).find_defs_and_refs is not _CellDSL.find_defs_and_refs
        else None
    )

    CELL_DSL_REGISTRY.register_detector(
        language=dsl.name,
        call_names=dsl.call_names,
        find_defs_and_refs=find_defs_and_refs,
    )

    def _entrypoint(source: str) -> object:
        return dsl.execute(source)

    _entrypoint.__name__ = dsl.name
    setattr(marimo, dsl.name, _entrypoint)
    if dsl.name not in marimo.__all__:
        marimo.__all__.append(dsl.name)

    broadcast_notification(
        DSLRegisteredNotification(
            dsl_name=dsl.name, call_names=dsl.call_names
        )
    )
