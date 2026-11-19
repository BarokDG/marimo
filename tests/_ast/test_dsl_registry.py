# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

import ast

import marimo
from marimo._ast import visitor
from marimo._ast.dsl import CellDSL
from marimo._ast.dsl_registry import register_cell_dsl
from marimo._ast.visitor import VariableData
from marimo._messaging.notification import DSLRegisteredNotification
from tests._ast.dsl_fixtures.wordmath import WordMathDSL
from tests.conftest import ExecReqProvider, MockedKernel


def test_register_cell_dsl_installs_entrypoint() -> None:
    register_cell_dsl(WordMathDSL())
    assert marimo.wordmath("one two three") == "six"  # type: ignore[attr-defined]
    assert "wordmath" in marimo.__all__


def test_visitor_detects_registered_dsl() -> None:
    register_cell_dsl(WordMathDSL())

    v = visitor.ScopedVisitor()
    mod = ast.parse('result = mo.wordmath("one two three")')
    v.visit(mod)

    assert v.language == "wordmath"
    assert v.defs == {"result"}
    assert v.refs == {"mo"}
    assert v.variable_data == {
        "result": [VariableData(kind="variable", required_refs={"mo"})]
    }


def test_find_defs_and_refs_hook_is_invoked() -> None:
    class FakeDSL(CellDSL):
        @property
        def name(self) -> str:
            return "fakedsl"

        def find_defs_and_refs(
            self,
            cell_visitor: visitor.ScopedVisitor,
            _node: ast.Call,
            _source: str,
        ) -> None:
            cell_visitor._define(
                None, "fake_table", VariableData(kind="variable")
            )

        def execute(self, source: str) -> str:
            return source

    register_cell_dsl(FakeDSL())

    v = visitor.ScopedVisitor()
    mod = ast.parse('result = mo.fakedsl("anything")')
    v.visit(mod)

    assert v.language == "fakedsl"
    assert "fake_table" in v.defs
    assert "result" in v.defs


def test_sql_detection_is_unaffected_by_registry() -> None:
    register_cell_dsl(WordMathDSL())

    v = visitor.ScopedVisitor()
    mod = ast.parse('df = mo.sql("select 1")')
    v.visit(mod)

    assert v.language == "sql"


async def test_register_cell_dsl_broadcasts_notification(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    await mocked_kernel.k.run(
        [
            exec_req.get(
                """
                from marimo._ast.dsl_registry import register_cell_dsl
                from tests._ast.dsl_fixtures.wordmath import WordMathDSL

                register_cell_dsl(WordMathDSL())
                """
            )
        ]
    )

    dsl_notifications = [
        op
        for op in mocked_kernel.stream.operations
        if isinstance(op, DSLRegisteredNotification)
    ]
    assert dsl_notifications == [
        DSLRegisteredNotification(
            dsl_name="wordmath", call_names=("mo.wordmath",)
        )
    ]
