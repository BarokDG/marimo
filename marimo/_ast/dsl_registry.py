# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from marimo._ast.dsl import CellDSL

_DSL = TypeVar("_DSL", bound="CellDSL")


def register_dsl_widget(name: str, dsl: _DSL) -> _DSL:
    """Announce a custom input widget for a custom-DSL-style cell.

    Cells calling the bare name `name` as `name("...")` -- where `name` is
    an ordinary Python callable bound to an ordinary variable, not a
    marimo-specific construct -- render with `dsl`'s custom widget instead
    of plain-text editing, if `dsl.input_widget_esm()` returns one. Returns
    `dsl` unchanged, so this can be called as
    `wordmath = register_dsl_widget("wordmath", WordMathDSL())`.

    This is purely a CodeMirror editing affordance: execution and
    reactivity already work via ordinary Python name references regardless
    of whether this is called, so there's nothing for correctness to depend
    on here, and nothing to clean up if the registering cell is later
    deleted (the cell calling `name(...)` will correctly error on its own,
    via marimo's normal "deleted variable" reactivity, with or without a
    stale widget association hanging around).
    """
    esm = dsl.input_widget_esm()
    if esm is None:
        return dsl

    from marimo._messaging.notification import (
        DSLRegisteredNotification,
        EsmSpec,
    )
    from marimo._messaging.notification_utils import broadcast_notification

    broadcast_notification(
        DSLRegisteredNotification(
            dsl_name=name,
            call_names=(name,),
            input_widget_esm_spec=EsmSpec.from_esm(esm),
        )
    )
    return dsl
