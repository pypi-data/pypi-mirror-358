import logging
import json
from datetime import datetime
import signal
from typing import Optional

import pandas as pd
from confluent_kafka import Consumer, Producer, KafkaError
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

from quartic_sdk.pipelines.settings import settings

logger = logging.getLogger(__name__)


class KafkaBatchConsumer:
    """
    Consumes batches from kafka, returns the batch as a DataFrame, and implements manual offset commits
    """

    def __init__(
        self,
        conf: dict,
        topics: list[str],
        batch_size: int = 50000,
        batch_timeout: int = 5,
        poll_timeout: int = 1,
    ):
        self.conf = conf
        self.consumer = Consumer(conf)
        self.consumer.subscribe(topics)
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.poll_timeout = poll_timeout
        self._running = True
        
    
    def close(self):
        """Gracefully close the consumer"""
        try:
            # Close the consumer
            print("Closing consumer...")
            self.consumer.close()
            logger.info("Consumer closed successfully")
        except Exception as e:
            logger.error(f"Error during consumer shutdown: {e}")
        finally:
            self._running = False

    def get(self) -> Optional[pd.DataFrame]:
        """
        Retrieve an event batch DataFrame
        Returns None if shutdown is in progress
        """
        try:
            messages = []
            # Block until we receive a message batch or shutdown signal
            while not messages and self._running:
                messages = self._consume_batch()
            
            if not self._running:
                logger.info("Shutdown in progress, returning None")
                return None
                
            return self._to_df(messages)
            
        except Exception as e:
            logger.error(f"Error in get(): {e}")
            self._running = False
            return None

    def commit(self):
        """
        Commit consumer offset
        """
        if self.conf.get("enable.auto.commit", True):
            logger.warning("Auto commit enabled. Ignoring commit attempt")
            return
        self.consumer.commit(asynchronous=False)

    def _consume_batch(self) -> list:
        messages = []
        #print(f"Consuming batch {self.batch_size=} {self.batch_timeout=} {self.poll_timeout=}")

        batch_start = datetime.now()
        while self._running and len(messages) < self.batch_size:
            try:
                message = self.consumer.poll(timeout=self.poll_timeout)
                
                if message is None:
                    if not messages:
                        batch_start = datetime.now()
                    time_elapsed = (datetime.now() - batch_start).total_seconds()
                    if time_elapsed >= self.batch_timeout:
                        logger.info("Batch timeout reached")
                        break
                    continue

                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Error during kafka message consumption: {message.error()}")
                    break

                messages.append(message)
                
            except Exception as e:
                logger.error(f"Error while polling messages: {e}", exc_info=True)
                self._running = False
                break

        return messages

    def _to_df(self, messages: list):
        messages = [
            {
                "value": m.value().decode("utf-8"),
                "key": m.key().decode("utf-8"),
                "topic": m.topic(),
                "partition": m.partition(),
                "offset": m.offset(),
                "timestamp": m.timestamp()
            }
            for m in messages
        ]
        return pd.DataFrame(messages)


class KafkaProducerFactory:
    producer = None
    aio_producer = None

    @classmethod
    def get_producer(cls):
        if cls.producer is None:
            cls.producer = Producer({
                **settings.get_kafka_config(),
                # Batching settings
                "batch.size": 65536,  # Increase batch size to 64KB
                "linger.ms": 5,       # Wait up to 5ms to batch messages
                "compression.type": "lz4",  # Use LZ4 compression for better performance
                
                # Buffer settings
                "queue.buffering.max.messages": 100000,  # Max messages in local buffer
                "queue.buffering.max.ms": 5,  # Maximum time to buffer locally
                "queue.buffering.max.kbytes": 1048576,  # 1GB local buffer
                
                # Performance settings
                "acks": "1",          # Wait for leader acknowledgment only
                "delivery.timeout.ms": 120000,  # Increase delivery timeout
                "request.timeout.ms": 30000,    # Increase request timeout
                
                # Socket settings
                "socket.send.buffer.bytes": 1048576,  # 1MB socket buffer
                "socket.receive.buffer.bytes": 1048576,
                
                # Additional throughput optimizations
                "message.send.max.retries": 3,
                "retry.backoff.ms": 100,
                "max.in.flight.requests.per.connection": 5
            })
        return cls.producer

    @classmethod
    async def get_aio_producer(cls) -> Optional[AIOKafkaProducer]:
        """Get or create an AIOKafkaProducer instance"""
        if cls.aio_producer is None:
            try:
                ssl_context = create_ssl_context(
                    cafile=settings.get_kafka_config().get('ssl.ca.location')
                )
                cls.aio_producer = AIOKafkaProducer(
                    bootstrap_servers=settings.get_kafka_config().get('bootstrap.servers'),
                    client_id='quartic-aio-producer',
                    
                    # Performance settings
                    linger_ms=5,       # 5ms linger
                    max_request_size=10485760,      # 10MB
                    max_batch_size=1048576,         # 1MB
                    # Delivery settings
                    acks=1,  # Wait for leader acknowledgment
                    request_timeout_ms=120000,
                    
                    # Retry settings
                    retry_backoff_ms=100,
                    
                    #ssl cert
                    ssl_context=ssl_context,
                    sasl_mechanism=settings.get_kafka_config().get('sasl.mechanism'),
                    security_protocol=settings.get_kafka_config().get('security.protocol'),
                    sasl_plain_username=settings.get_kafka_config().get('sasl.username'),
                    sasl_plain_password=settings.get_kafka_config().get('sasl.password'),
                )
                
                await cls.aio_producer.start()
                logger.info("AIOKafkaProducer initialized successfully")
                return cls.aio_producer
                
            except Exception as e:
                logger.error(f"Failed to initialize AIOKafkaProducer: {e}")
                raise

        return cls.aio_producer

    @classmethod
    async def close_aio_producer(cls):
        """Gracefully close the AIOKafkaProducer"""
        if cls.aio_producer is not None:
            try:
                await cls.aio_producer.stop()
                cls.aio_producer = None
                logger.info("AIOKafkaProducer closed successfully")
            except Exception as e:
                logger.error(f"Error closing AIOKafkaProducer: {e}")
                raise
