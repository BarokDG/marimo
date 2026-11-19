# Copyright 2026 Marimo. All rights reserved.
"""A trivial DSL used only to validate `CellDSL`/`register_cell_dsl`.

Sums whitespace-separated number-words and renders the result back as a
number-word, e.g. `"one two three"` -> `"six"`. Deliberately has no
cross-cell refs/defs, to prove the `CellDSL` no-op defaults are sufficient
for the simplest possible DSL.
"""

from __future__ import annotations

from marimo._ast.dsl import CellDSL

_WORD_TO_NUM = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}
_NUM_TO_WORD = {v: k for k, v in _WORD_TO_NUM.items()}


def run(source: str) -> str:
    tokens = source.strip().split()
    values = [_WORD_TO_NUM[token] for token in tokens]
    total = sum(values)
    return _NUM_TO_WORD[total]


class WordMathDSL(CellDSL):
    @property
    def name(self) -> str:
        return "wordmath"

    def execute(self, source: str) -> str:
        return run(source)
