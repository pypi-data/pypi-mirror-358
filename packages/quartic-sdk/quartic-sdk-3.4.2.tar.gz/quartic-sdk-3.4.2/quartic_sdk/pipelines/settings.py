import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Settings:
    # Kafka
    broker_url: str = os.environ.get("KAFKA_BROKER_URL", None)
    kafka_consumer_group: str = os.environ.get('KAFKA_CONSUMER_GROUP', 'scripts-0')
    kafka_sasl_mechanism: str = os.environ.get("KAFKA_SASL_MECHANISM", None)
    kafka_security_protocol: str = os.environ.get("KAFKA_SECURITY_PROTOCOL", None)
    kafka_sasl_jaas_config: str = os.environ.get("KAFKA_SASL_JAAS_CONFIG", None)
    kafka_sasl_username: str = os.environ.get("KAFKA_SASL_USERNAME", None)
    kafka_sasl_password: str = os.environ.get("KAFKA_SASL_PASSWORD", None)
    kafka_ssl_truststore_location: str = os.environ.get(
        "KAFKA_SSL_TRUSTSTORE_PASSWORD", None
    )
    kafka_ssl_truststore_type: str = os.environ.get("KAFKA_SSL_TRUSTSTORE_TYPE", None)
    kafka_enable_ssl: bool = (
        os.environ.get("KAFKA_ENABLE_SSL", "true").lower() == "true"
    )
    truststore_password_file: Optional[str] = os.environ.get(
        "KAFKA_SSL_TRUSTSTORE_PASSWORD_LOCATION", None
    )
    kafka_ssl_ca_location: str = os.environ.get(
        "KAFKA_SSL_CA_LOCATION", "/strimzi-cluster-cluster-ca-cert/ca.crt"
    )
    # Connector states
    internal_sink_state_directory = os.environ.get(
        "INTERNAL_SINK_STATE_DIRECTORY", "/app/connector_data/internal/state/"
    )
    mapping_connector_state_directory = os.environ.get(
        "MAPPING_CONNECTOR_STATE_DIRECTORY", "/app/connector_data/mapping/state/"
    )
    default_connector_state_directory = os.environ.get(
        "DEFAULT_CONNECTOR_STATE_DIRECTORY", "/app/connector_data/default/state/"
    )
    telemetry_topic = os.environ.get("TELEMETRY_TOPIC", "flat_telemetry")

    @property
    def truststore_password(self):
        truststore_password = None
        if not truststore_password or not os.path.exists(self.truststore_password_file):
            logger.warning(
                f"Skipping trust store password setup. File {self.truststore_password_file} not found."
            )
        else:
            with open(self.truststore_password_file, "r") as f:
                truststore_password = f.read()

        return truststore_password

    def get_kafka_config(self):
        config = {
            "bootstrap.servers": self.broker_url,
        }
        if self.kafka_enable_ssl:
            config = {
                **config,
                "sasl.mechanism": self.kafka_sasl_mechanism,
                "security.protocol": self.kafka_security_protocol,
                "sasl.username": self.kafka_sasl_username,
                "sasl.password": self.kafka_sasl_password,
                "ssl.ca.location": self.kafka_ssl_ca_location,
            }
        return config


settings = Settings()
