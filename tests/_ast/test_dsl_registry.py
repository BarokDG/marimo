# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from marimo._ast.dsl import CellDSL
from marimo._ast.dsl_registry import register_dsl_widget
from marimo._messaging.notification import DSLRegisteredNotification
from tests.conftest import ExecReqProvider, MockedKernel


class _WidgetedDSL(CellDSL):
    def execute(self, source: str) -> str:
        return source

    def input_widget_esm(self) -> str:
        return "export default class {}"


class _WidgetlessDSL(CellDSL):
    def execute(self, source: str) -> str:
        return source


async def test_register_dsl_widget_broadcasts_notification(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    await mocked_kernel.k.run(
        [
            exec_req.get(
                """
                from marimo._ast.dsl_registry import register_dsl_widget
                from tests._ast.test_dsl_registry import _WidgetedDSL
                register_dsl_widget("wordmath", _WidgetedDSL())
                """
            )
        ]
    )

    dsl_notifications = [
        op
        for op in mocked_kernel.stream.operations
        if isinstance(op, DSLRegisteredNotification)
    ]
    assert dsl_notifications
    notification = dsl_notifications[-1]
    assert notification.dsl_name == "wordmath"
    assert notification.call_names == ("wordmath",)
    assert notification.input_widget_esm_spec is not None


async def test_register_dsl_widget_with_no_widget_broadcasts_nothing(
    mocked_kernel: MockedKernel, exec_req: ExecReqProvider
) -> None:
    await mocked_kernel.k.run(
        [
            exec_req.get(
                """
                from marimo._ast.dsl_registry import register_dsl_widget
                from tests._ast.test_dsl_registry import _WidgetlessDSL
                register_dsl_widget("querydb", _WidgetlessDSL())
                """
            )
        ]
    )

    dsl_notifications = [
        op
        for op in mocked_kernel.stream.operations
        if isinstance(op, DSLRegisteredNotification)
    ]
    assert dsl_notifications == []


def test_register_dsl_widget_returns_the_dsl_instance() -> None:
    dsl = _WidgetedDSL()
    assert register_dsl_widget("wordmath", dsl) is dsl


def test_register_dsl_widget_without_a_running_kernel_is_a_no_op() -> None:
    # No kernel context on this thread: `broadcast_notification` catches
    # `ContextNotInitializedError` internally, so this must not raise.
    register_dsl_widget("wordmath", _WidgetedDSL())
