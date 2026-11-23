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

    `WordMathDSL` itself lives in `wordmath_extension.py`, a plain sibling
    module imported below -- not defined inline -- to demonstrate that a
    DSL extension can be authored and shipped like any other importable
    Python package, with the notebook only importing it and calling
    `register_cell_dsl(...)`.
    """)


@app.cell
def _():
    from marimo._ast.dsl_registry import register_cell_dsl
    from wordmath_extension import WordMathDSL

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
    two = 'two'
    return (two,)


@app.cell
def _(mo, two: str):
    mo.wordmath(f"one {two} four")


if __name__ == "__main__":
    app.run()
