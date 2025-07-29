import logging
from typing import Tuple

from quartic_sdk.graphql_client import GraphqlClient
from quartic_sdk.pipelines.sinks.internal.operations.handlers.base import (
    OperationHandler,
)
from quartic_sdk.pipelines.sinks.internal.operations.operations import (
    GQLQuery,
)

logger = logging.getLogger(__name__)


class GQLQueryHandler(OperationHandler[GQLQuery]):
    @classmethod
    def get_optype(cls):
        return GQLQuery

    def handle(
        self, operations: list[GQLQuery]
    ) -> Tuple[list[GQLQuery], list[GQLQuery]]:
        client = GraphqlClient.get_graphql_client_from_env()
        success, failed = [], []

        for op in operations:
            try:
                response = client.execute_query(op.query, op.variables)
                if op.is_ok is None or op.is_ok(response):
                    success.append(op)
                else:
                    failed.append(op)
            except Exception:
                logger.exception(f"Failed to execute operation {op}")
                failed.append(op)

        return success, failed
