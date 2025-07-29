from typing import Callable
import json
import pandas as pd
from pydantic import BaseModel
from datetime import datetime
from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.pipelines.sinks.base_sink import CONNECTOR_CLASS
from quartic_sdk.pipelines.connector_app import BaseConfig
from quartic_sdk.pipelines.sinks.internal.internal_sink import InternalPlatformSink
from quartic_sdk.pipelines.sinks.internal.operations.operations import InternalOperation, TagTelemetry

class TelemetrySinkConfig(BaseModel, BaseConfig):
    connector_id: int


def default_transformation(df: pd.DataFrame, state: dict) -> list[InternalOperation]:
    """
    Default transformation for Telemetry Internal Sink.
    """
    import json
    from quartic_sdk.graphql_client import GraphqlClient
    from quartic_sdk.pipelines.sinks.internal.operations.operations import TagTelemetry
    connector_id = state.get("connector_id")
    if not connector_id:
        raise ValueError("connector_id is required")
    if not "tags" in state:
        # Create GOL Client
        client = GraphqlClient.get_graphql_client_from_env()
        # Fetch tags only if not already in state
        query = f"""
            query MyQuery {{
                        Tag(edgeConnector: {connector_id}) {{
                            id
                            name
                        }}
            }}
        """
        response = client.execute_query(query, {})
        state["tags"] = {tag["name"]: tag["id"] for tag in response["data"]["Tag"]}
    tag_map = state["tags"]
    ops = []
    values = df.value.apply(json.loads)
    for row in values:
        if row["node"] in tag_map:
            ops.append(
                TagTelemetry(
                    timestamp=row["timestamp"],
                    value=row["value"],
                    edgeconnector=connector_id,
                    tag=tag_map[row["node"]]
                )
            )
    return ops


class TelemetrySink(AsyncKafkaProducerMixin, InternalPlatformSink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transformation: Callable[
            [pd.DataFrame, dict], list[InternalOperation]
        ] = kwargs.get('transformation', default_transformation)
        self.connector_class: str = CONNECTOR_CLASS.Telemetry_Internal.value
        self.connector_config: TelemetrySinkConfig = kwargs.get("connector_config")
        self.state["connector_id"] = self.connector_config.connector_id
        self.start_kafka_worker()
    
    def close(self):
        super().close()
        self.logger.info("Closing TelemetrySink")
        self.stop_kafka_worker()
    
    def test_config(self):
        try:
            data = {
                "value": json.dumps({
                    "timestamp": datetime.now().timestamp() * 1000,
                    "node": "test",
                    "value": "0"
                })
            }
            df = pd.DataFrame([data])
            self.process_records(df)
            return "Connection successful"
        except Exception as e:
            return f"Failed to write data: {e}"
