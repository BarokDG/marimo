# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from marimo._ast.dsl_registry import register_cell_dsl
from tests._ast.dsl_fixtures.wordmath import WordMathDSL
from tests.conftest import ExecReqProvider, MockedKernel


async def test_wordmath_cell_runs_and_reacts(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    register_cell_dsl(WordMathDSL())

    await mocked_kernel.k.run(
        [
            exec_req.get("import marimo as mo"),
            (
                result_req := exec_req.get(
                    'result = mo.wordmath("one two three")'
                )
            ),
        ]
    )
    assert mocked_kernel.k.globals["result"] == "six"

    # Editing the literal and re-running the same cell id reruns through
    # the normal exec()/reactivity pipeline, same as any Python cell.
    await mocked_kernel.k.run(
        [
            exec_req.get_with_id(
                result_req.cell_id, 'result = mo.wordmath("four five")'
            )
        ]
    )
    assert mocked_kernel.k.globals["result"] == "nine"


async def test_wordmath_downstream_cell_reacts(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    register_cell_dsl(WordMathDSL())

    await mocked_kernel.k.run(
        [
            exec_req.get("import marimo as mo"),
            (
                result_req := exec_req.get(
                    'result = mo.wordmath("one two three")'
                )
            ),
            exec_req.get("doubled = result + result"),
        ]
    )
    assert mocked_kernel.k.globals["doubled"] == "sixsix"

    await mocked_kernel.k.run(
        [
            exec_req.get_with_id(
                result_req.cell_id, 'result = mo.wordmath("nine")'
            )
        ]
    )
    assert mocked_kernel.k.globals["doubled"] == "ninenine"
