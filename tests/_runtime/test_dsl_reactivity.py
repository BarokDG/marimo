# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from marimo._runtime.commands import DeleteCellCommand
from tests.conftest import ExecReqProvider, MockedKernel


async def test_deleting_cell_that_defines_a_callable_breaks_consumer_live(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    """A "custom DSL" is now just an ordinary Python callable bound to an
    ordinary variable -- no marimo-specific registration involved. This
    characterizes pre-existing marimo behavior (no new production code
    under test): deleting the cell that defines the callable immediately
    breaks every cell that calls it, live, with no restart needed --
    exactly the guarantee the old `register_cell_dsl`/`mo.<name>`
    monkeypatch approach failed to provide.
    """
    k = mocked_kernel.k
    owner_req = exec_req.get("def wordmath(source): return source.upper()")
    consumer_req = exec_req.get('result = wordmath("hi")')

    await k.run([owner_req, consumer_req])
    assert k.globals["result"] == "HI"

    await k.delete_cell(DeleteCellCommand(cell_id=owner_req.cell_id))

    assert "wordmath" not in k.globals
    if k.lazy():
        assert k.graph.cells[consumer_req.cell_id].stale
        await k.run([consumer_req])

    assert "result" not in k.globals
    consumer_cell = k.graph.cells[consumer_req.cell_id]
    assert isinstance(consumer_cell.exception, NameError)


async def test_deleting_cell_that_defines_cross_cell_dsl_state_breaks_consumer_live(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    """Mirrors the `querydb` example: a DSL's "connection" is just a plain
    object bound to a plain variable, so deleting the cell that creates it
    breaks consumers live, with no special-casing anywhere.
    """
    k = mocked_kernel.k
    owner_req = exec_req.get(
        """
        class QueryDB:
            def __init__(self, rows):
                self.rows = rows

            def __call__(self, query):
                return self.rows

        main = QueryDB([{"id": 1}])
        """
    )
    consumer_req = exec_req.get('result = main("SELECT * FROM users")')

    await k.run([owner_req, consumer_req])
    assert k.globals["result"] == [{"id": 1}]

    await k.delete_cell(DeleteCellCommand(cell_id=owner_req.cell_id))

    assert "main" not in k.globals
    if k.lazy():
        assert k.graph.cells[consumer_req.cell_id].stale
        await k.run([consumer_req])

    consumer_cell = k.graph.cells[consumer_req.cell_id]
    assert isinstance(consumer_cell.exception, NameError)
