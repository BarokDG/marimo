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

    Same **in-progress, unshipped** `CellDSL`/`register_cell_dsl` mechanism as
    the word-math and draw-math examples, but demonstrating cross-cell state:
    one cell "connects" to a dummy in-memory database, a separate cell uses
    the DSL's own tiny query syntax to query it.

    Unlike `mo.sql(...)`, which can take a live `engine=` object because it
    has its own hand-written parser, custom DSLs today only ever receive a
    plain string -- so the connection here is addressed **by name inside the
    query text**, not by passing a live Python object between cells.
    """)


@app.cell
def _():
    class DummyDB:
        """An in-memory "database": just a dict of table name -> rows."""

        def __init__(self, tables: dict[str, list[dict[str, object]]]):
            self.tables = tables

    DUMMY_DBS: dict[str, DummyDB] = {}

    def connect_dummy_db(name: str) -> DummyDB:
        """Create (or replace) a named dummy DB connection, seeded with a
        small `users` table, and register it for `mo.querydb(...)` to find
        by name."""
        db = DummyDB(
            tables={
                "users": [
                    {"id": 1, "name": "Alice", "age": 30},
                    {"id": 2, "name": "Bob", "age": 25},
                    {"id": 3, "name": "Carol", "age": 35},
                ],
            }
        )
        DUMMY_DBS[name] = db
        return db

    return DummyDB, DUMMY_DBS, connect_dummy_db


@app.cell
def _(DUMMY_DBS):
    from marimo._ast.dsl import CellDSL
    from marimo._ast.dsl_registry import register_cell_dsl

    class QueryDBDSL(CellDSL):
        """Queries a dummy DB connected (by name) in another cell.

        A deliberately tiny, hand-parsed two-line query language, not a SQL
        subset:

        ```
        USE <connection name>
        SELECT <cols | *> FROM <table> [WHERE <col> = <value>]
        ```

        No quoting, no `AND`/`OR`, no joins, and `WHERE` supports exactly one
        plain string-equality check. No cross-cell refs/defs -- the
        connection name is just text inside the query, looked up at
        execution time.
        """

        @property
        def name(self) -> str:
            return "querydb"

        def execute(self, source: str) -> list[dict[str, object]]:
            lines = [line.strip() for line in source.strip().splitlines() if line.strip()]

            if not lines or not lines[0].startswith("USE "):
                raise ValueError("First line must be `USE <connection name>`")
            db_name = lines[0].removeprefix("USE ").strip()
            if db_name not in DUMMY_DBS:
                raise ValueError(
                    f"Not connected to {db_name!r} -- call "
                    f"connect_dummy_db({db_name!r}) in another cell first"
                )
            db = DUMMY_DBS[db_name]

            if len(lines) < 2 or not lines[1].upper().startswith("SELECT "):
                raise ValueError(
                    "Second line must be `SELECT <cols|*> FROM <table> "
                    "[WHERE <col> = <value>]`"
                )
            query = lines[1][len("SELECT ") :]
            select_part, _, rest = query.partition(" FROM ")
            cols = [c.strip() for c in select_part.split(",")]
            table_part, _, where_part = rest.partition(" WHERE ")
            table = table_part.strip()
            if table not in db.tables:
                raise ValueError(f"Unknown table {table!r}")
            rows = db.tables[table]

            if where_part:
                col, _, value = where_part.partition("=")
                col = col.strip()
                value = value.strip()
                rows = [r for r in rows if str(r.get(col)) == value]

            if cols != ["*"]:
                rows = [{c: r[c] for c in cols} for r in rows]
            return rows

    register_cell_dsl(QueryDBDSL())


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    First connect, then query -- re-run this notebook top to bottom. Try
    changing the `WHERE` value, or querying a connection name that was never
    connected (e.g. `USE missing`) to see the error.
    """)


@app.cell
def _(connect_dummy_db):
    conn = connect_dummy_db("main")
    return (conn,)


@app.cell
def _(mo):
    mo.querydb(r"""
    USE main
    SELECT * FROM users
    """)


@app.cell
def _(mo):
    mo.querydb(r"""
    USE main
    SELECT name FROM users WHERE id = 2
    """)


if __name__ == "__main__":
    app.run()
