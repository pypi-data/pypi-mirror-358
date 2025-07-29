from quartic_sdk.pipelines.connector_app import ConnectorApp, CONNECTOR_CLASS, get_truststore_password
import os
import json


SINK_CONNECTOR_PROTOCOLS = [CONNECTOR_CLASS.Http.value, 
                            CONNECTOR_CLASS.HttpSoap.value, 
                            CONNECTOR_CLASS.External.value, 
                            CONNECTOR_CLASS.Custom.value, 
                            CONNECTOR_CLASS.EventHub.value]

class SourceApp(ConnectorApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_type: str = "SOURCE"
        self.connector_class: str = CONNECTOR_CLASS.Custom.value
    
    def get_write_data(self, batch_df):
        data = batch_df.apply(lambda x: (str(1), json.dumps(x.to_dict())), axis=1).to_list()
        return data

    def write_data(self, spark, batch_df):
        data = self.get_write_data(batch_df)
        if all(False for _ in data):
            return

        sdf = spark.createDataFrame(data,['key', 'value'])
        sdf.write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_URL', 'broker:9092')) \
        .option("topic", self.topic_to_push_to) \
        .option("kafka.security.protocol", os.environ.get('KAFKA_SECURITY_PROTOCOL')) \
        .option("kafka.sasl.mechanism", os.environ.get('KAFKA_SASL_MECHANISM')) \
        .option("kafka.sasl.jaas.config", f'org.apache.kafka.common.security.scram.ScramLoginModule required username="{os.environ.get("KAFKA_SASL_USERNAME")}" password="{os.environ.get("KAFKA_SASL_PASSWORD")}";') \
        .option("kafka.ssl.endpoint.identification.algorithm", os.environ.get('KAFKA_SSL_ALGORITHM', ' ')) \
        .option("kafka.ssl.truststore.location", os.environ.get('KAFKA_SSL_TRUSTSTORE_LOCATION'))\
        .option("kafka.ssl.truststore.password", get_truststore_password())\
        .option("kafka.ssl.truststore.type", os.environ.get('KAFKA_SSL_TRUSTSTORE_TYPE')) \
        .save()

