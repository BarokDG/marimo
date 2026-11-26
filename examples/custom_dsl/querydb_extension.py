"""A standalone, importable marimo custom-DSL extension.

`QueryDB` implements `CellDSL` and demonstrates cross-cell DSL state: an
instance holds a live connection (`DummyDB`), called directly as
`main("SELECT ...")`. Because it's just an ordinary Python object bound to
an ordinary variable, it gets full dependency-graph reactivity for free --
deleting the cell that creates it breaks every cell that calls it, live,
with no special-casing anywhere in marimo.

Editing this file requires restarting the notebook's kernel to pick up
changes (Python caches imports) -- there's no reload mechanism wired up
here.
"""

from marimo._ast.dsl import CellDSL


class DummyDB:
    """An in-memory "database": just a dict of table name -> rows."""

    def __init__(self, tables: dict[str, list[dict[str, object]]]):
        self.tables = tables


def make_dummy_db(**tables: list[dict[str, object]]) -> DummyDB:
    return DummyDB(tables=tables)


class QueryDB(CellDSL):
    """Queries a connected dummy DB. Call the instance directly, e.g.
    `main("SELECT * FROM users")`.

    Implements `CellDSL` -- a documented contract for DSL authors -- but
    never calls `register_dsl_widget`: that hook is entirely optional, and
    this DSL has no custom input widget, just the default plain-text
    editing.

    A deliberately tiny, hand-parsed query language, not a SQL subset:

    ```
    SELECT <cols | *> FROM <table> [WHERE <col> = <value>]
    ```

    No quoting, no `AND`/`OR`, no joins, and `WHERE` supports exactly one
    plain string-equality check.
    """

    def __init__(self, db: DummyDB) -> None:
        self._db = db

    def execute(self, source: str) -> list[dict[str, object]]:
        lines = [
            line.strip()
            for line in source.strip().splitlines()
            if line.strip()
        ]
        if not lines or not lines[0].upper().startswith("SELECT "):
            raise ValueError(
                "Query must be `SELECT <cols|*> FROM <table> "
                "[WHERE <col> = <value>]`"
            )
        query = lines[0][len("SELECT ") :]
        select_part, _, rest = query.partition(" FROM ")
        cols = [c.strip() for c in select_part.split(",")]
        table_part, _, where_part = rest.partition(" WHERE ")
        table = table_part.strip()
        if table not in self._db.tables:
            raise ValueError(f"Unknown table {table!r}")
        rows = self._db.tables[table]

        if where_part:
            col, _, value = where_part.partition("=")
            col = col.strip()
            value = value.strip()
            rows = [r for r in rows if str(r.get(col)) == value]

        if cols != ["*"]:
            rows = [{c: r[c] for c in cols} for r in rows]
        return rows
