import logging
import inspect
from typing import Type

from quartic_sdk.pipelines.sinks.internal.operations.operations import InternalOperation
from quartic_sdk.pipelines.sinks.internal.operations import handlers
from quartic_sdk.pipelines.sinks.internal.operations.handlers.base import (
    OperationHandler,
)

ALL_HANDLERS: list[Type[OperationHandler]] = list(
    filter(
        lambda c: inspect.isclass(c)
        and c != OperationHandler
        and issubclass(c, OperationHandler),
        [getattr(handlers, a) for a in dir(handlers)],
    )
)
logging.info(f"Detected operation handlers: {[h.__name__ for h in ALL_HANDLERS]}")


def get_handler(operation: InternalOperation, queue_message=None) -> OperationHandler:
    for handler_cls in ALL_HANDLERS:
        if handler_cls.get_optype() == operation.__class__:
            return handler_cls(queue_message=queue_message)
    raise NotImplementedError(f"No handler for for operation {operation}")
