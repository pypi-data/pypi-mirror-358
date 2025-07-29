from typing import Callable
from itertools import groupby

import pandas as pd
from quartic_sdk.pipelines.sinks.base_sink import KafkaSinkApp
from quartic_sdk.pipelines.sinks.internal.operations.operations import InternalOperation
from quartic_sdk.pipelines.sinks.internal.operations.handlers.utils import get_handler


class InternalPlatformSink(KafkaSinkApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transformation: Callable[[pd.DataFrame, dict], list[InternalOperation]] = kwargs.get('transformation', None)

    def write_data(self, operations: list[InternalOperation]):
        self.logger.info(f"Process {len(operations)} operations")
        if not operations:
            return
        handler = get_handler(queue_message=self.queue_message, operation=operations[0])
        
        success, failed = handler.handle(operations)
        assert not failed, f"Failed operations: {failed}"

    def process_records(self, data: pd.DataFrame):
        if not self.transformation:
            self.logger.exception(
                f"Unexpected empty transformation in internal sink {self.transformation}"
            )
            return

        operations = self.transformation(data, self.state)
        
        if not operations:
            self.logger.warning(f"Empty opreations return from transformation")
            return

        grouped_operations = self.__group_operations(operations)
        self.logger.debug(f"Operations: {grouped_operations}")
        for op_group in grouped_operations:
            self.write_data(op_group)

    def __group_operations(self, operations: list[InternalOperation]):
        """
        Returns adjacent groups of operations.

        Example:
        Grouping operations [A, A, B, C, A]
        Returns: [[A, A], [B], [C], [A]]

        This is to preserve the order of operations during evaluation.
        """
        groups = groupby(operations, lambda op: op.optype)
        return [list(group) for _, group in groups]


