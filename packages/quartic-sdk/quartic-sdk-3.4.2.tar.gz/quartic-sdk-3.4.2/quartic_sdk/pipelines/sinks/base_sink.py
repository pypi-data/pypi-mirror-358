import signal
from typing import final
from abc import abstractmethod
import pandas as pd
import os
from quartic_sdk.pipelines.connector_app import ConnectorApp, CONNECTOR_CLASS, get_truststore_password
from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.utilities.kafka import KafkaBatchConsumer
from quartic_sdk.pipelines.settings import settings
from quartic_sdk.pipelines.helpers.connector_state_mixin import ConnectorStateMixin
from pydantic import validator


SINK_CONNECTOR_PROTOCOLS = [
    CONNECTOR_CLASS.Http.value,
    CONNECTOR_CLASS.HttpSoap.value,
    CONNECTOR_CLASS.External.value,
    CONNECTOR_CLASS.Custom.value,
    CONNECTOR_CLASS.EventHub.value,
    CONNECTOR_CLASS.Telemetry_Internal.value,
    CONNECTOR_CLASS.Batch_Internal.value,
    CONNECTOR_CLASS.Telemetry_Internal.value,
    CONNECTOR_CLASS.Batch_Internal.value,
]


class SinkApp(ConnectorApp,ConnectorStateMixin):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kafka_topics = kwargs.get('kafka_topics', None)
        self.STATE_BASE_DIR = settings.default_connector_state_directory
        self.connector_type: str = "SINK"
        self.connector_class: str = CONNECTOR_CLASS.Custom.value
        self._running = True
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
    
    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        self.logger.info(f"Received signal {signum}. Starting graceful shutdown SinkApp.")
        self._running = False
        raise Exception("Shutdown")

    @abstractmethod
    def start(self, id: int, kafka_topics: list[str], source: list[int]):
        raise NotImplemented

    @validator("connector_class")
    def validate_option(cls, v):
        assert v in SINK_CONNECTOR_PROTOCOLS, f"Invalid protocol for Sink Connector {v}"
        return v

    def process_records(self, batch_df):
        if self.transformation:
            with self.open_state(self.id) as state:
                batch_df = self.transformation(batch_df, state)
        self.write_data(batch_df)
    
    def close(self):
        self.logger.info("Closing SinkApp")
        self._running = False

class KafkaSinkApp(SinkApp):
    def __init__(self, **kwargs):
        self.batch_size = kwargs.get('batch_size', 50000)
        super().__init__(**kwargs)
        
    def start(self):
        try:
            
            consumer = KafkaBatchConsumer(conf={
                **settings.get_kafka_config(),
                "group.id": f"sink_{self.id}",
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                # Performance optimization settings
                'fetch.min.bytes': 65536,          # 64KB minimum fetch size
                'fetch.max.bytes': 52428800,       # 50MB max fetch
                'max.partition.fetch.bytes': 1048576,  # 1MB per partition
                 # Performance settings
                'socket.receive.buffer.bytes': 1048576,  # 1MB socket buffer
                'socket.send.buffer.bytes': 1048576,
                # Batching settings
                'max.poll.interval.ms': 300000,    # 5 minutes
                # Session settings
                'enable.auto.commit': False,  # Manual commit for better control
                'auto.offset.reset': 'latest',  # Start from earliest if no offset
                # Consumer group settings
                'session.timeout.ms': 45000,       # 45 seconds
                'heartbeat.interval.ms': 15000,    # 15 seconds
                # Additional optimizations
                'queued.min.messages': 10000,      # Min messages to queue
                'queued.max.messages.kbytes': 1048576,  # 1GB queue buffer
            
            }, topics=self.kafka_topics, batch_size=self.batch_size)
            while True:
                df = consumer.get()
                if not self._running:  # Shutdown signal received
                    break
                self.process_records(df)
                consumer.commit()
        finally:
            consumer.close()
            self.close()