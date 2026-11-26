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

    A "custom DSL" is nothing more than an ordinary Python callable bound
    to an ordinary variable. There's no marimo-specific registration step
    for *execution* -- `wordmath` is a `CellDSL` instance, called directly
    like any other callable, and gets full reactivity for free: editing or
    deleting the cell that creates it correctly breaks every cell that
    calls it, live, with no special-casing anywhere in marimo. `CellDSL`
    itself is just a documented contract for DSL authors to implement --
    marimo never looks it up or dispatches through it.

    `WordMathDSL` itself lives in `wordmath_extension.py`, a plain sibling
    module imported below -- not defined inline -- to demonstrate that a
    DSL can be authored and shipped like any other importable Python
    package.

    The *only* optional, separate piece is a custom input widget
    (replacing plain-text editing with the terminal-styled box below) --
    purely a CodeMirror editing affordance, registered via
    `register_dsl_widget`. It has no bearing on execution or reactivity,
    which already work without it.
    """)


@app.cell
def _():
    from marimo._ast.dsl_registry import register_dsl_widget
    from wordmath_extension import WordMathDSL

    wordmath = register_dsl_widget("wordmath", WordMathDSL())
    return (wordmath,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Try editing the string below (e.g. to `"four five"`) and watch the
    cell -- and the one after it -- react, exactly like any other
    Python cell.
    """)


@app.cell
def _():
    two = "two"
    return (two,)


@app.cell
def _(two: str, wordmath):
    wordmath(f"one {two} four")


if __name__ == "__main__":
    app.run()
