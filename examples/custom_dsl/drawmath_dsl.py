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
    # Custom DSL cells: a draw-math example

    Same idea as the word-math example -- `drawmath` is a `CellDSL`
    instance, called directly, with no registration needed for execution
    or reactivity -- but with a draw-to-input custom widget instead of a
    text box: click or drag across cells on a tiny pixel grid to draw a
    digit, recognized against a handful of hardcoded templates --
    deliberately the simplest thing that can draw and recognize digits, not
    real digit recognition.

    `DrawMathDSL` itself lives in `drawmath_extension.py`, a plain sibling
    module imported below -- not defined inline -- to demonstrate that a
    DSL can be authored and shipped like any other importable Python
    package.
    """)


@app.cell
def _():
    from drawmath_extension import DrawMathDSL
    from marimo._ast.dsl_registry import register_dsl_widget

    drawmath = register_dsl_widget("drawmath", DrawMathDSL())
    return (drawmath,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Click or drag across cells to draw a digit, then **Add digit** to
    recognize it and append it to the running list below the grid. Try
    drawing a couple of
    digits -- the cell re-runs and shows the updated sum, exactly like any
    other Python cell reacting to an edit.

    (The cell's code must stay a bare `drawmath(...)` call, with no
    variable assignment, for the widget to render instead of plain text --
    a current limitation of the generic custom-DSL parser, unlike
    `mo.sql(...)` cells which do support `df = mo.sql(...)`.)
    """)


@app.cell
def _(drawmath):
    drawmath(r"""
    1 7 7 2 2
    """)


@app.cell
def _(drawmath):
    drawmath(r"""
    1 7 7
    """)


if __name__ == "__main__":
    app.run()
