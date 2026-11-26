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
    # Custom DSL cells: a connect-then-query example

    A "custom DSL" is nothing more than an ordinary Python object bound to
    an ordinary variable, called directly. This example demonstrates
    cross-cell DSL state: one cell "connects" to a dummy in-memory
    database, other cells use the DSL's own tiny query syntax to query it
    -- by calling the connection object itself, e.g. `main("SELECT ...")`.

    Because `main` is just a normal variable, this gets full reactivity
    for free: **delete the cell below that defines `main`, and every cell
    that calls `main(...)` immediately breaks, live, with no special-casing
    anywhere in marimo** -- exactly the guarantee a `mo.sql(...)`-style
    monkeypatched-module-attribute approach can't provide, since deleting
    that kind of registration leaves the module attribute installed and
    the notebook silently broken until a fresh kernel.

    Two independent connections (`main`, `secondary`) are registered below
    under no name at all -- there's no DSL "name" to coordinate, since each
    is just its own Python object.

    `QueryDB`/`DummyDB`/`make_dummy_db` live in `querydb_extension.py`, a
    plain sibling module imported below -- not defined inline -- to
    demonstrate that a DSL can be authored and shipped like any other
    importable Python package.
    """)


@app.cell
def _():
    from querydb_extension import QueryDB, make_dummy_db

    return QueryDB, make_dummy_db


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Try editing a connection's seed data below and re-running its cell --
    the query cells that call it react automatically. Then try deleting
    the `main = QueryDB(...)` cell entirely and watch its query cells
    break immediately, live.
    """)


@app.cell
def _(QueryDB, make_dummy_db):
    main = QueryDB(
        make_dummy_db(
            users=[
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
                {"id": 3, "name": "Carol", "age": 35},
            ]
        )
    )
    return (main,)


@app.cell
def _(QueryDB, make_dummy_db):
    secondary = QueryDB(
        make_dummy_db(
            products=[
                {"id": 1, "sku": "A1", "price": 9.99},
                {"id": 2, "sku": "B2", "price": 19.99},
            ]
        )
    )
    return (secondary,)


@app.cell
def _(main):
    main(r"""SELECT * FROM users""")


@app.cell
def _(main):
    main(r"""SELECT name FROM users WHERE id = 2""")


@app.cell
def _(secondary):
    secondary(r"""SELECT * FROM products""")


if __name__ == "__main__":
    app.run()
