# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Custom DSL cells: a word-math example

    This notebook demos an **in-progress, unshipped** mechanism for
    registering custom non-SQL "DSL cells" -- generalizing the way
    `mo.sql(...)` cells work today so other DSLs can plug in the same
    way, without marimo core needing to special-case each one.

    `CellDSL` and `register_cell_dsl` live in **private** modules
    (`marimo._ast.dsl`, `marimo._ast.dsl_registry`) and are **not** a
    public API yet -- this notebook is for trying the mechanism out,
    not a feature to build on.
    """)


@app.cell
def _():
    from marimo._ast.dsl import CellDSL
    from marimo._ast.dsl_registry import register_cell_dsl

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

    class WordMathDSL(CellDSL):
        """Sums whitespace-separated number-words, e.g.

        `"one two three"` -> `"six"`. No cross-cell refs/defs, so it uses
        `CellDSL`'s no-op defaults for everything except `name`/`execute`.
        """

        @property
        def name(self) -> str:
            return "wordmath"

        def execute(self, source: str) -> str:
            tokens = source.strip().split()
            total = sum(_WORD_TO_NUM[token] for token in tokens)
            return _NUM_TO_WORD[total]

    register_cell_dsl(WordMathDSL())


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Try editing the string below (e.g. to `"four five"`) and watch the
    cell -- and the one after it -- react, exactly like any other
    Python cell.
    """)


@app.cell
def _():
    two = 'three'
    return (two,)


@app.cell
def _(mo, two: str):
    mo.wordmath(f"one {two} four")


if __name__ == "__main__":
    app.run()
