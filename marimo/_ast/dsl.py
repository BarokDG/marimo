# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import ast

    from marimo._ast.cell import CellImpl
    from marimo._ast.visitor import ScopedVisitor


class CellDSL(ABC):
    """A pluggable custom-DSL cell type.

    Subclass this and pass an instance to `register_cell_dsl` to let marimo
    recognize `mo.<name>(...)` calls as a distinct cell language, with
    optional cross-cell ref/def extraction and execution -- the same
    mechanism SQL cells (`mo.sql(...)`) use internally, made available to
    other DSLs.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short name, e.g. `"wordmath"`. Becomes `mo.<name>` and the
        `CellImpl.language` tag used for matched cells."""

    @property
    def call_names(self) -> tuple[str, ...]:
        """Fully-qualified call names that mark a cell as this DSL.

        Matched the same way as SQL's call detection: `node.func` must be a
        plain `ast.Attribute` on a bare `ast.Name`, with exactly one
        positional string/f-string argument. Default: `("mo.<name>",)`.
        """
        return (f"mo.{self.name}",)

    def find_defs_and_refs(
        self, _visitor: ScopedVisitor, _node: ast.Call, _source: str
    ) -> None:
        """Register cross-cell defs/refs found in `source`.

        Call `visitor._define(...)` / `visitor._add_ref(...)` as needed.
        Default: no-op. Most DSLs -- like a pure string-to-value transform --
        have no table/variable-like entities inside their source string, and
        get ordinary Python reactivity for free via the cell's assignment
        target(s).
        """
        return

    @abstractmethod
    def execute(self, source: str) -> Any:
        """Run the DSL on `source`. Becomes the body of the generated
        `mo.<name>(...)` callable."""

    def render(self, _cell: CellImpl) -> str | None:
        """Optional codegen round-trip hook.

        Default: `None`, meaning "the cell's literal source is already
        valid Python" -- true for any DSL whose surface syntax is
        `mo.<name>("...")`.
        """
        return None

    def input_widget_esm(self) -> str | None:
        """Optional ESM module (as a string) rendering this DSL's input
        surface, replacing plain-text editing.

        Narrow contract, NOT anywidget's model/trait-sync protocol: the
        module's default export is called once per cell instance with
        `{el, code, setCode}` -- `code` is the cell's current unwrapped DSL
        body; `setCode(next)` rewrites it. No comm, no continuous
        bidirectional sync. Default: `None` (plain-text editing).
        """
        return None
