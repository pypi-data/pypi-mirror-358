import base64
import marshal
import types
from typing import Any

from quartic_sdk.pipelines.config.opcua import OPCUASinkConfig, OPCUASourceConfig
from quartic_sdk.pipelines.connector_app import ExternalApp
from quartic_sdk.pipelines.sinks.eventhub_sink import (
    EventHubSink,
    EventHubConfig as EventHubSinkConfig
)
from quartic_sdk.pipelines.sinks.http_sink import HttpConfig, HttpSink
from quartic_sdk.pipelines.sinks.internal.batch_sink import BatchSink, BatchSinkConfig
from quartic_sdk.pipelines.sinks.internal.telemetry_sink import TelemetrySink, TelemetrySinkConfig
from quartic_sdk.pipelines.sinks.model_mapping_sink import ModelMappingConfig, ModelMappingSink
from quartic_sdk.pipelines.sinks.opcua_sink import OPCUASinkApp
from quartic_sdk.pipelines.settings import settings
from quartic_sdk.pipelines.sources.deltav_source import DeltaVConfig, DeltaVSource
from quartic_sdk.pipelines.sources.eventhub_source import (
    EventHubSource,
    EventHubConfig as EventHubSourceConfig
)
from quartic_sdk.pipelines.sources.opcua_source import OpcuaSource


def get_connector_config(connector_data):
    """
    Creates and returns a configuration object based on the connector type and class.

    Args:
        connector_data (ConnectorData): ConnectorApp object

    Returns:
        Any: A configuration object of one of the following types:
            - OPCUASourceConfig/OPCUASinkConfig (for OPCUA connections)
            - EventHubSourceConfig/EventHubSinkConfig (for Azure Event Hub)
            - DeltaVConfig (for DeltaV SQL)
            - HttpConfig (for HTTP connections)
            - BatchSinkConfig (for batch internal connections)
            - TelemetrySinkConfig (for telemetry internal connections)
            - ModelMappingConfig (for model mapping connections)
    """
    connector_config = None
    if connector_data.connector_class == 'OPCUA':
        config = {
            "username": connector_data.connector_config.get('username'),
            "password": connector_data.connector_config.get('password'),
            "host_url": connector_data.connector_config.get('host_url'),
            "application_uri": connector_data.connector_config.get('application_uri'),
        }
        if connector_data.connector_type == 'SOURCE':
            config['node_ids'] = connector_data.connector_config.get('node_ids')
            connector_config = OPCUASourceConfig(**config)
        else:
            connector_config = OPCUASinkConfig(**config)
    elif connector_data.connector_class == 'AZURE_EVENT_HUB':
        config = {
            "connection_string": connector_data.connector_config.get('connection_string')
        }
        if connector_data.connector_type == 'SOURCE':
            if connector_data.connector_config.get('consumer_group'):
                config['consumer_group'] = connector_data.connector_config['consumer_group']
            connector_config = EventHubSourceConfig(**config)
        else:
            connector_config = EventHubSinkConfig(**config)
    elif connector_data.connector_class == 'DELTA_V_SQL':
        connector_config = DeltaVConfig(
            username=connector_data.connector_config.get('username'),
            password=connector_data.connector_config.get('password'),
            host_url=connector_data.connector_config.get('host_url'),
            port=connector_data.connector_config.get('port'),
            db_name=connector_data.connector_config.get('db_name'),
            db_timezone=connector_data.connector_config.get('db_timezone'),
            query_frequency=connector_data.connector_config.get('query_frequency')
        )
    elif connector_data.connector_class == 'HTTP':
        connector_config = HttpConfig(
            username=connector_data.connector_config.get('username'),
            password=connector_data.connector_config.get('password'),
            endpoint=connector_data.connector_config.get('endpoint'),
            auth_type=connector_data.connector_config.get('auth_type'),
            access_token=connector_data.connector_config.get('access_token'),
            refresh_token=connector_data.connector_config.get('refresh_token'),
            refresh_endpoint=connector_data.connector_config.get('refresh_endpoint'),
            group_messages=connector_data.connector_config.get('group_messages'),
            headers=connector_data.connector_config.get('headers'),
            timeout=connector_data.connector_config.get('timeout')
        )
    elif connector_data.connector_class == 'BATCH_INTERNAL':
        connector_config = BatchSinkConfig(
            site_id=connector_data.connector_config.get('site_id'),
            product_id=connector_data.connector_config.get('product_id')
        )
    elif connector_data.connector_class == 'TELEMETRY_INTERNAL':
        connector_config = TelemetrySinkConfig(
            connector_id=connector_data.connector_config.get('connector_id')
        )
    elif connector_data.connector_class == 'MODEL_MAPPING':
        connector_config = ModelMappingConfig(
            tag_attribute_mapping=connector_data.connector_config.get('tag_attribute_mapping'),
            asset_id=connector_data.connector_config.get('asset_id'),
            alias_attributes=connector_data.connector_config.get('alias_attributes'),
            procedure_id=connector_data.connector_config.get('procedure_id')
        )
    return connector_config


def load_function_from_string(base64_string):
    code_bytes = base64.b64decode(base64_string) 
    code_object = marshal.loads(code_bytes) 
    return types.FunctionType(code_object, globals()) 
    

def get_connector_obj(connector_data, test_run: bool = False) -> Any:
    """
    Creates and returns a connector object based on the connector data configuration.

    Args:
        connector_data (ConnectorData): ConnectorApp object

    Returns:
        Any: A connector object instance of one of the following types:
            - Opcua/OPCUASinkApp (for OPCUA connections)
            - EventHubSource/EventHubSink (for Azure Event Hub)
            - Deltav (for DeltaV SQL)
            - ExternalApp (for external connections)
            - HttpSink (for HTTP connections)
            - BatchSink (for batch internal connections)
            - TelemetrySink (for telemetry internal connections)
            - ModelMappingSink (for model mapping connections)
    """
    connector_config = get_connector_config(connector_data)
    args = {
        "id": connector_data.id,
        "name":connector_data.name,
        "source": connector_data.source_connectors if connector_data.id else [],
        "app_config": connector_data.app_config,
        "connector_config": connector_config,
        "connector_class": connector_data.connector_class,
        "connector_type": connector_data.connector_type
    }
    connector_obj = None
    if connector_data.connector_class == 'OPCUA':
        if connector_data.connector_type == 'SOURCE':
            connector_obj = OpcuaSource(**args)
        else:
            connector_obj = OPCUASinkApp(**args)
    elif connector_data.connector_class == 'AZURE_EVENT_HUB':
        if connector_data.connector_type == 'SINK':
            connector_obj = EventHubSink(**args)
        else:
            connector_obj = EventHubSource(**args)
    elif connector_data.connector_class == 'DELTA_V_SQL':
        connector_obj = DeltaVSource(**args)
    elif connector_data.connector_class == 'EXTERNAL':
        connector_obj = ExternalApp(**args) 
    elif connector_data.connector_class == 'HTTP':
        connector_obj = HttpSink(
            id=connector_data.id,
            connector_config=connector_config
        )
    elif connector_data.connector_class == 'BATCH_INTERNAL':
        connector_obj = BatchSink(
            id=connector_data.id,
            connector_config=connector_config
        )
    elif connector_data.connector_class == 'TELEMETRY_INTERNAL':
        connector_obj = TelemetrySink(
            id=connector_data.id,
            topic_to_push=settings.telemetry_topic,
            connector_config=connector_config
        )
    elif connector_data.connector_class == 'MODEL_MAPPING':
        connector_obj = ModelMappingSink(
            id=connector_data.id,
            connector_config=connector_config
        )
    if connector_data.connector_type in ['SINK', 'SOURCE_AND_SINK']:
        if connector_data.connector_config.get('transformation'):
            connector_obj.transformation = load_function_from_string(
                connector_data.connector_config.get('transformation')
            )
    if not test_run:
        if connector_data.connector_type == 'SINK':
            connector_obj.kafka_topics = connector_data.kafka_topics
        elif connector_data.connector_type == 'SOURCE':
            connector_obj.topic_to_push = connector_data.kafka_topics[0]
        elif connector_data.connector_type == 'SOURCE_AND_SINK':
            connector_obj.topic_to_push = f"Connector_{connector_data.id}"
            connector_obj.kafka_topics = [
                topic for topic in connector_data.kafka_topics if topic != f"Connector_{connector_data.id}"
            ]
    connector_obj.test_run = test_run
    return connector_obj
