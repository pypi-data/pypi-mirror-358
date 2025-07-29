from quartic_sdk.pipelines.sources.base_source import SourceApp
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS, get_truststore_password, BaseConfig
from pydantic import BaseModel
import os
import json
from azure.eventhub import EventHubConsumerClient
import pandas as pd
from quartic_sdk.pipelines.connector_app import ConnectorApp
from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.pipelines.connector_app import BaseConfig

class EventHubConfig(BaseConfig):
    def __init__(self, connection_string: str, consumer_group: str = '$Default'):
        self.connection_string = connection_string
        self.consumer_group = consumer_group


class EventHubSource(AsyncKafkaProducerMixin, ConnectorApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_type = "SOURCE"
        self.connector_class = CONNECTOR_CLASS.EventHub.value
        self.last_processed_offset = {}
    
    def process_records(self, batch_df: pd.DataFrame):
        """
        Process the records from the EventHub

        Args:
            batch_df (pd.DataFrame): Batch of records to process
        """
        if batch_df.empty:
            return
        if self.transformation:
            batch_df = self.transformation(batch_df)
        data = iter(batch_df.apply(lambda x: (str(self.id), x.value), axis=1).to_list())
        if self.test_run:
            print(data)
        else:
            for k,v in data:
                self.queue_message((k,v))


    def start(self):
        """
        Start the EventHubSource
        """
        client = EventHubConsumerClient.from_connection_string(
            self.connector_config.connection_string,
            consumer_group=self.connector_config.consumer_group
        )
        self.last_processed_offset = self.state['last_processed_offset'] if\
                                        'last_processed_offset' in self.state else {}
        
        def on_event_batch(partition_context, events):
            df = pd.DataFrame({'value' : [e.body_as_str(encoding="UTF-8") for e in events]})
            self.process_records(df)
            self.last_processed_offset[partition_context.partition_id] = events[-1].sequence_number
            
        self.start_kafka_worker()
        
        try:
            client.receive_batch(on_event_batch=on_event_batch, starting_position=self.last_processed_offset)
        except (KeyboardInterrupt, Exception) as e:
            self.logger.error(f"Error in EventHub processing: {e}")
            self.close()
            client.close()
            self.stop_kafka_worker()
            self.logger.info("EventHubSource closed")

    def test_config(self):
        try:
            client = EventHubConsumerClient.from_connection_string(
                self.connector_config.connection_string,
                consumer_group=self.connector_config.consumer_group
            )
            client.get_eventhub_properties()
            client.close()
            return "Connection successful"
        except Exception as e:
            return f"Failed to get eventhub properties: {e}"
