import asyncio
from datetime import datetime
import random
import time
from asyncua import Client, ua
from pydantic import BaseModel
from pytz import timezone
from queue import Queue
import threading
from functools import partial
import logging

from quartic_sdk.pipelines.connector_app import AppConfig
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.utilities.opcua import get_client, get_security_string
from quartic_sdk.utilities.utils import to_epoch
from quartic_sdk.pipelines.connector_app import ConnectorApp
import json

# OPC UA async streamer class
class OpcuaSource(AsyncKafkaProducerMixin, ConnectorApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_type = "SOURCE"
        self.connector_class = CONNECTOR_CLASS.Opcua.value
        self.connector_config = kwargs.get('connector_config', None) 
        self.client = None
        self.app_config = AppConfig(driver_memory_request="1g")
        self.connected = False
        self.retry_delay = 10
        self.kafka_push_batch_size = kwargs.get('kafka_push_batch_size', 40000)
    
    async def datachange_notification(self, node, val, data):
        timestamp = None
        if data.monitored_item.Value.SourceTimestamp:
            timestamp = data.monitored_item.Value.SourceTimestamp
        elif data.monitored_item.Value.ServerTimestamp:
            timestamp = data.monitored_item.Value.ServerTimestamp
        if timestamp:
            json_data = {
                'timestamp': to_epoch(timestamp, timezone_string="UTC"),
                'node': node.nodeid.to_string(),
                'value': val
            }
            if self.test_run:
                self.logger.info(f'source data : {json_data}')
            else:
                self.queue_message(json_data)
    
    async def status_change_notification(self, status: ua.StatusChangeNotification):
        """
        This method is called whenever a subscription status changes.

        Args:
            status (ua.StatusChangeNotification): _description_
        """
        print(f"Subscription status changed: {status}")
        if status:
            print("Subscription lost. Attempting to reconnect...")
            await self.reconnect()
        
    async def subscribe_to_nodes(self):
        """
        This method subscribes to the nodes specified in the connector config.
        """
        subscription = await self.client.create_subscription(100, self)
        for node_id in self.connector_config.node_ids:
            try:
                node = self.client.get_node(node_id)
                await subscription.subscribe_data_change(node,sampling_interval=500)
            except Exception:
                self.logger.exception(f"Error while subscribing to {node_id}")
    
    async def connect(self):
        """
        This method connects to the OPC UA server.
        """
        self.client = get_client(self.connector_config)
        security_string = get_security_string(self.connector_config)
        if security_string:
            self.logger.info(f"Using security string {security_string}")
            await self.client.set_security_string(security_string)
        await self.client.connect()
        self.connected = True
    
    async def reconnect(self):
        """
        This method reconnects to the OPC UA server.
        """
        retry_count = 0
        while True:
            try:
                await self.disconnect()
                await asyncio.sleep(self.retry_delay)
                await self.connect()
                await self.subscribe_to_nodes()
                self.logger.info("Reconnection successful")
                return
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Reconnection attempt {retry_count} failed: {str(e)}")
    
    async def disconnect(self):
        """
        This method disconnects from the OPC UA server.
        """
        if self.client:
            await self.client.disconnect()
        self.connected = False

    async def connection_loop(self):
        """
        This method is the main loop for the connection.
        """
        while True:
            try:
                if not self.connected:
                    await self.connect()
                    await self.subscribe_to_nodes()
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.exception(f"Error occurred: {e}")
                await self.disconnect()
                self.logger.warning(f"Reconnecting to OPC UA server in {self.retry_delay} seconds")
                await asyncio.sleep(self.retry_delay)
                

    def start(self):
        """Start the connector"""
        self.start_kafka_worker()  # Start Kafka worker
        
        try:
            asyncio.run(self.connection_loop())
        finally:
            self.stop_kafka_worker()  # Stop Kafka worker
        
    def test_config(self):
        try:
            asyncio.run(self.connect())
            return "Connection successful"
        except Exception as e:
            return f"Failed to get opcua properties: {e}"

