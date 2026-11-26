# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CellDSL(ABC):
    """Documented contract for a custom DSL, implemented as a plain Python
    callable.

    This is *not* a registry or dispatch mechanism -- marimo never looks up
    or calls through this interface. A cell recognizes a DSL purely by
    calling an ordinary variable as a function (e.g. `wordmath("...")`),
    which already gets full dependency-graph reactivity via marimo's
    ordinary Python name-reference tracking, with or without this base
    class. `CellDSL` exists only to give DSL authors (and
    `register_dsl_widget`) a predictable, documented shape to implement.
    """

    @abstractmethod
    def execute(self, source: str) -> Any:
        """Execute the DSL on `source`."""

    def __call__(self, source: str) -> Any:
        """Makes instances directly callable, e.g. `wordmath("...")`.

        Implement `execute`, not this -- `__call__` just forwards to it, so
        marimo's cells can call a DSL as an ordinary function with no
        dispatch mechanism involved.
        """
        return self.execute(source)

    def input_widget_esm(self) -> str | None:
        """Optional ESM module (as a string) rendering this DSL's input
        surface, replacing plain-text editing. See `register_dsl_widget`.

        Narrow contract, NOT anywidget's model/trait-sync protocol: the
        module's default export is a class extending `HTMLElement` (a
        Custom Element), and it must also have a named `tagName` export --
        the hyphenated tag marimo registers it under (e.g. `"wordmath-
        widget"`). marimo constructs one instance per cell, sets `.code`
        (the cell's current unwrapped DSL body) and `.setCode` (a function
        that rewrites it) on it, then mounts it -- rendering and lifecycle
        (e.g. `connectedCallback`) are the class's own responsibility,
        exactly like any custom element. No comm, no continuous
        bidirectional sync. Default: `None` (plain-text editing).
        """
        return None
