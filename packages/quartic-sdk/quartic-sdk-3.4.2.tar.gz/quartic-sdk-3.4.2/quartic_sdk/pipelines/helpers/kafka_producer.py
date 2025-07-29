import os
import json
import logging
from datetime import datetime, timedelta
import random
import time

from quartic_sdk.utilities.kafka import KafkaProducerFactory

import asyncio
import threading
from queue import Queue, Full
import logging
from typing import Optional, Any


class AsyncKafkaProducerMixin:
    """Mixin class for async Kafka producer functionality"""
    
    def __init__(self, **kwargs):
        
        self.producer = None
        self.data_queue = Queue(maxsize=1000000)
        self.running = True
        self.loop = None
        self.last_print_time = time.time()
        self.flush_interval = 10
        self.topic_to_push = kwargs.get('topic_to_push', None)
        self.worker_thread = None
        self.batch_size = kwargs.get('batch_size', 40000)
        self.messages_sent = 0
        self.partitions = []
        super().__init__(**kwargs)
        
        

    async def setup_producer(self):
        """Initialize the Kafka producer"""
        from quartic_sdk.utilities.kafka import KafkaProducerFactory
        self.logger.info("Setting up producer")
        self.producer = await KafkaProducerFactory.get_aio_producer()
        self.logger.info(f"Producer initialized. Getting partitions for {self.topic_to_push}")
        self.partitions = await self.producer.partitions_for(self.topic_to_push)
        self.logger.info("Partitions fetched")

    async def produce_to_kafka(self, batch_data):
        """Async method to produce to Kafka"""
        if not self.producer:
            self.logger.info("Producer not initialized, initializing...")
            await self.setup_producer()
            
        batch = self.producer.create_batch()
        # timestamp in epoch milliseconds
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        for data in batch_data:
            if isinstance(data, dict):
                value = json.dumps(data).encode('utf-8')
                key = str(self.id).encode('utf-8')
                batch.append(key=key, value=value, timestamp=timestamp)
            elif isinstance(data, tuple):
                batch.append(key=data[0].encode('utf-8'), 
                             value=json.dumps(data[1]).encode('utf-8'),
                             timestamp=timestamp)
            else:
                self.logger.error(f"Unexpected data type: {type(data)}")

        partition = random.choice(tuple(self.partitions))
        self.messages_sent += batch.record_count()
        await self.producer.send_batch(batch, self.topic_to_push, partition=partition)

    def serialize_message(self, data: Any) -> bytes:
        """Override this method to implement custom serialization"""
        import json
        return json.dumps(data).encode('utf-8')

    def kafka_worker(self):
        """Worker thread to process queued data and send to Kafka"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            # Initialize the producer in the worker thread
            self.logger.info("Initializing producer in Kafka worker thread")
            self.loop.run_until_complete(self.setup_producer())
            
            self.logger.info("Producer initialized in Kafka worker thread")
            while self.running:
                try:
                    batch_data = []
                    
                    # Collect messages for batch
                    while len(batch_data) < self.batch_size and self.running:
                        try:
                            data = self.data_queue.get_nowait()
                            batch_data.append(data)
                            self.data_queue.task_done()
                        except Exception:
                            break
                    
                    if batch_data:
                        # Process batch in the thread's event loop
                        self.loop.run_until_complete(self.produce_to_kafka(batch_data))
                    else:
                        # If no messages, sleep briefly
                        time.sleep(0.01)
                    if time.time() - self.last_print_time >= self.flush_interval:
                        self.loop.run_until_complete(self.producer.flush())
                        self.logger.info(f"Sent {self.messages_sent} messages to Kafka in last {self.flush_interval} seconds. "
                                f"Queue size: {self.data_queue.qsize()}. ")
                        self.last_print_time = time.time()
                        self.messages_sent = 0
                    if self.test_run:
                        break
                        
                except Exception as e:
                    self.logger.exception(f"Error in kafka worker: {e}")
                    
        finally:
            if self.producer:
                self.loop.run_until_complete(self.flush_producer_and_close())
            self.loop.close()

    def start_kafka_worker(self):
        """Start the Kafka worker thread"""
        if not self.worker_thread:
            self.logger.info("Starting Kafka worker thread")
            self.worker_thread = threading.Thread(target=self.kafka_worker)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            self.logger.info("Kafka worker thread started.")

    def stop_kafka_worker(self):
        """Stop the Kafka worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=30)
            self.worker_thread = None
            self.logger.info("Kafka worker thread stopped")

    async def flush_producer_and_close(self):
        """Flush and close the Kafka producer"""
        if self.producer:
            try:
                self.logger.info("Flushing producer...")
                await self.producer.flush()
                await self.producer.stop()
                self.producer = None
                self.logger.info("Producer closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing producer: {e}")
                raise

    def queue_message(self, data: Any):
        """Queue a message for async processing"""
        try:
            self.data_queue.put(data, timeout=0.1)
        except Full:
            self.logger.warning("Queue is full, message dropped") 


class KafkaConnector(object):
    """
    Class to upload data to Kafka
    """

    def __init__(self):
        self.kafka_producer = KafkaProducerFactory.get_producer()
        self.last_flushed = datetime.now()
        self.flush_interval = timedelta(seconds=1)
        self.max_retries = 3
        self.retry_delay = 2
        
    def upload_bulk(self, datapoints, topic, key) -> None:
        """
        Upload a bulk of datapoints to Kafka
        """
        for datapoint in datapoints:
            self.upload_data(datapoint, topic, key)

    def upload_data(self, datapoint, topic, key) -> None:
        """
        Transform message and write to Kafka with retry logic
        """


        # Try to produce with retries
        for attempt in range(self.max_retries):
            try:
                self.kafka_producer.produce(
                    topic, 
                    value=json.dumps(datapoint),
                    key=str(key)
                )
                
                # Poll more aggressively to clear the queue
                self.kafka_producer.poll(0)
                
                # Get number of messages waiting to be delivered
                queued_msgs = len(self.kafka_producer)  # This is the correct way to get queue size
                
                # If queue is getting full, force a flush
                if queued_msgs > 5000:  # Adjust this threshold as needed
                    logging.warning(f"Producer queue getting full ({queued_msgs} messages), forcing flush")
                    self.kafka_producer.flush(timeout=1)
                    self.last_flushed = datetime.now()
                
                break  # Success, exit retry loop
                
            except BufferError as e:
                if attempt < self.max_retries - 1:  # Don't sleep on last attempt
                    time.sleep(self.retry_delay)
                    # Force a flush to clear the queue
                    try:
                        self.kafka_producer.flush(timeout=1)
                        self.last_flushed = datetime.now()
                    except Exception as flush_err:
                        logging.error(f"Error while force-flushing: {flush_err}")
                else:
                    logging.error(f"Failed to produce message after {self.max_retries} attempts: {e}")
                    raise
