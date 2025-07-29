from pydantic import BaseModel
from quartic_sdk.pipelines.sinks.base_sink import KafkaSinkApp
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from azure.eventhub import EventHubProducerClient, TransportType
from azure.eventhub import EventData
from quartic_sdk.pipelines.connector_app import BaseConfig


class EventHubConfig(BaseConfig):
    def __init__(self, **kwargs):
        self.connection_string: str = kwargs.get('connection_string', None)

class EventHubSink(KafkaSinkApp):
    """
    EventHub sink application.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_class = CONNECTOR_CLASS.EventHub.value
        self.connector_config = kwargs.get('connector_config', None)
    
    def write_data(self, batch_df):
        if batch_df.empty:
            return
        producer = EventHubProducerClient.\
                    from_connection_string(
                        conn_str=self.connector_config.connection_string,
                        transport_type=TransportType.AmqpOverWebsocket
                    )
        messages_df = batch_df
        event_data_batch = producer.create_batch()
        count = 0
        for _, row in messages_df.iterrows():
            try:
                event_data_batch.add(EventData(row['value']))
                count += 1
            except Exception as e:
                producer.send_batch(event_data_batch)
                event_data_batch = producer.create_batch()
                event_data_batch.add(EventData(row['value']))
                count = 1
        if count > 0:
            producer.send_batch(event_data_batch)
        producer.close()
    
    def test_config(self):
        producer = EventHubProducerClient.\
                    from_connection_string(conn_str=self.connector_config.connection_string)
        try:
            producer.get_eventhub_properties()
            producer.close()
            return "Connection successful"
        except Exception as e:
            return f"Failed to get eventhub properties: {e}"
        
