import logging
import json
from typing import Tuple, Type

from confluent_kafka import Producer

from quartic_sdk.pipelines.sinks.internal.operations.handlers.base import (
    OperationHandler,
)
from quartic_sdk.pipelines.sinks.internal.operations.operations import TagTelemetry


logger = logging.getLogger(__name__)
TELEMETRY_TOPIC = "flat_telemetry"


class TagTelemetryHandler(OperationHandler[TagTelemetry]):
    @classmethod
    def get_optype(cls):
        return TagTelemetry

    def handle(self, operations: list[TagTelemetry]):
        success, failed = [], []

        for op in operations:
            json_data = {
                    "timestamp": op.timestamp,
                    "tag": op.tag,
                    "value": op.value,
                    "edgeconnector": op.edgeconnector,
                }
            self.queue_message(json_data)
        return success, failed

