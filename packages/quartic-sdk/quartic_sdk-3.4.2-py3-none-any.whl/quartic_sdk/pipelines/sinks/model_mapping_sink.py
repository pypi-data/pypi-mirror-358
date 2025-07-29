import json

import pandas as pd
from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.pipelines.sinks.base_sink import KafkaSinkApp
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.connector_app import BaseConfig


class ModelMappingConfig(BaseConfig):
    def __init__(self, **kwargs):
        self.tag_attribute_mapping: dict = kwargs.get('tag_attribute_mapping', {})
        self.asset_id: int = kwargs.get('asset_id', None)
        self.alias_attributes: list[str] = kwargs.get('alias_attributes', [])
        self.procedure_id: int = kwargs.get('procedure_id', None)


class ModelMappingSink(AsyncKafkaProducerMixin, KafkaSinkApp):
    """
    Model Mapping sink application.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_type = 'SOURCE_AND_SINK'
        self.connector_class = CONNECTOR_CLASS.ModelMapping.value
        self.connector_config = kwargs.get('connector_config', None)
    
    def start(self):
        self.start_kafka_worker()
        super().start()

    def close(self):
        super().close()
        self.logger.info("Closing ModelMappingSink")
        self.stop_kafka_worker()
    
    def write_data(self, batch_df):
        if batch_df.empty:
            return
        values = batch_df.value.apply(json.loads).to_list()
        values_df = pd.DataFrame(values)
        valid_df = values_df[values_df['node'].isin(self.connector_config.tag_attribute_mapping.keys())]
        for _, row in valid_df.iterrows():
            value = json.loads(row.to_json())
            value[self.connector_config.tag_attribute_mapping[row['node']]] = row['value']
            del value['node']
            self.queue_message((row['node'], value))
    
    def test_config(self):
        return "Connection successful"