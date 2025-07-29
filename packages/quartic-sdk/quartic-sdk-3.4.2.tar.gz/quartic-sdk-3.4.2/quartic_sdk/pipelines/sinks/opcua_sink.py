import time
import json
from typing import Optional

from .base_sink import KafkaSinkApp
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.config.opcua import OPCUASecurityConfig, OPCUASinkConfig
from quartic_sdk.utilities.opcua import get_client, get_security_string
from pydantic import BaseModel, PrivateAttr
import pandas as pd
from asyncua.ua import VariantType, StatusChangeNotification
from asyncua.common.ua_utils import string_to_variant
from asyncua.ua import DataValue
import asyncio
from datetime import datetime
from asyncua.ua.uaerrors import BadNodeIdUnknown, BadNodeIdInvalid

MAX_RETRY_ATTEMPTS = 3


class OPCUASinkApp(KafkaSinkApp):
    """
    OPCUA write sink application.

    Sample event:
        {
          "node": "ns=3;i=1907",
          "value": "21.2",
          "timestamp": "1715145600000"
        }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_class = CONNECTOR_CLASS.Opcua.value
        self.connector_config = kwargs.get('connector_config', None)
        self.client = None
        self.is_connected = False
        self.nodes: dict = {}
        self.retry_delay = 10


    async def connect(self):
        """
        This method connects to the OPC UA server.
        """
        while not self.is_connected:
            try:
                print("Connecting to OPC UA server")
                self.client = get_client(self.connector_config)
                security_string = get_security_string(self.connector_config)
                if security_string:
                    self.client.set_security_string(security_string)
                await self.client.connect()
                self.logger.info(
                    f"Connected to OPC UA server at {self.connector_config.host_url}"
                )
                self.is_connected = True
            except Exception as e:
                print(f"Failed to connect to OPC UA server : {e}")
                print(f"Retrying in {self.retry_delay} seconds")
                if self._running and not self.test_run:
                    time.sleep(self.retry_delay)
                else:
                    raise e

    async def get_opcua_node(self, node_id: str) -> dict:
        """
        This method gets the OPC UA node.

        Args:
            node_id (str): The node id.

        Returns:
            dict: The OPC UA node.
        """
        if node_id not in self.nodes:
            node = self.client.get_node(node_id)
            datatype = None
            try:
                datatype = await node.read_data_type_as_variant_type()
            except (AttributeError,BadNodeIdUnknown, BadNodeIdInvalid) as e:
                print(f"Failed to get data type for node {node_id}")
            self.nodes[node_id] = {"node": node, "datatype": datatype}
        return self.nodes[node_id]

    async def disconnect(self):
        """
        This method disconnects from the OPC UA server.
        """
        if self.client:
            await self.client.disconnect()
        self.is_connected = False
        self.client = None
        self.nodes = {}
            
    async def write_data(self,batch_df: pd.DataFrame):
        """
        This method writes data to the OPC UA server.

        Args:
            batch_df (pd.DataFrame): The batch of data to write.
        """
        await self.connect()
        messages = [json.loads(m) for m in batch_df["value"]]
        for message in messages:
            node_name = message["node"]
            value = message["value"]
            timestamp = message["timestamp"]
            try:
                nodeobj = await self.get_opcua_node(node_name)
                if nodeobj['datatype']:
                    data_value = DataValue(string_to_variant(value, nodeobj['datatype']),
                                           SourceTimestamp=datetime.fromtimestamp(int(timestamp) / 1000))
                    await nodeobj['node'].set_value(data_value)
                    print(f"Wrote value {value} to node {node_name}")
                else:
                    self.logger.error(f"Failed to get data type for node {node_name}")
            except Exception as e:
                self.logger.exception(f"Failed to write data to node {node_name}")
                await self.disconnect()
                await self.connect()
        await self.disconnect()
        

    def process_records(self, batch_df: pd.DataFrame):
        if batch_df is None or batch_df.empty:
            return
        if self.transformation:
            batch_df = self.transformation(batch_df)
        if not self.test_run:
            asyncio.run(self.write_data(batch_df))

    def test_config(self):
        try:
            asyncio.run(self.connect())
            return "Connection successful"
        except Exception as e:
            return f"Failed to get opcua properties: {e}"
