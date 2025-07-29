from quartic_sdk.pipelines.sources.base_source import SourceApp
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS,  BaseConfig
from pydantic import BaseModel
from hashlib import md5
import os
import json
import time
import pyodbc
from datetime import datetime
import pytz
import pandas as pd
from typing import Any

from quartic_sdk.pipelines.helpers.kafka_producer import AsyncKafkaProducerMixin
from quartic_sdk.pipelines.connector_app import ConnectorApp


class DeltaVConfig(BaseConfig):
    def __init__(self,                 
        username: str,
        password: str,
        host_url: str,
        port: str,
        db_name: str,
        db_timezone: str,
        query_frequency: int = 30
    ):
        self.username = username
        self.password = password
        self.host_url = host_url
        self.port = port
        self.db_name= db_name
        self.db_timezone = db_timezone
        self.query_frequency = query_frequency
            

class DeltaVSource(AsyncKafkaProducerMixin, ConnectorApp):
    """
    Deltav source class
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_class = CONNECTOR_CLASS.DeltaV.value
        self.connector_type = "SOURCE"
        self.tz: Any = None
        self.timestamp_columns: list = ["starttime", "endtime"]

    def process_records(self, batch_df: pd.DataFrame) -> None:
        """
        Process the records from the batch dataframe

        Args:
            batch_df (pd.DataFrame): DeltaV batch dataframe
        """
        if batch_df.empty:
            return
        self.logger.info(f"Processing {len(batch_df)} records")
        latest = pytz.utc.localize(datetime.utcnow(), is_dst=None).astimezone(self.tz).strftime("%Y-%m-%d %X")
        completed_df = batch_df[batch_df['endtime'] <= latest]
        if not completed_df.empty:
            self.state['last_processed_timestamp'] = completed_df['endtime'].max().strftime("%Y-%m-%d %X")

        # Convert timestamps to milliseconds in one operation per column
        batch_df[self.timestamp_columns] = (batch_df[self.timestamp_columns]
            .astype('int64')
            .floordiv(1e6)
            .astype('int64'))
        
        data = self.get_write_data(batch_df)
        
        if self.test_run:
            print(data)
        else:
            for k,v in data:
                self.queue_message((k, v))
        
    def get_write_data(self, batch_df: pd.DataFrame) -> list:
        """
        Get the data to write to Kafka

        Args:
            batch_df (pd.DataFrame): DeltaV batch dataframe

        Returns:
            list: Data to write to Kafka
        """
        last_seen_data = self.state['last_seen_data'] if 'last_seen_data' in self.state else {}
        data = []
        
        for _, row in batch_df.iterrows():
            row_hash = md5(row.to_json().encode()).hexdigest()
            if row_hash in last_seen_data:
                continue
            last_seen_data[row_hash] = [row['starttime'], row['endtime']]
            data.append((row['uniqueid'], json.loads(row.to_json())))
        self.state['last_seen_data'] = last_seen_data
        return data

    def get_connection(self) -> pyodbc.Connection:
        """
        Get the connection to the database

        Returns:
            pyodbc.Connection: Database connection
        """
        conn_str = f'''DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={self.connector_config.host_url};
            DATABASE={self.connector_config.db_name};
            UID={self.connector_config.username};
            PWD={self.connector_config.password};
            Encrypt=yes;
            TrustServerCertificate=yes'''
        return pyodbc.connect(conn_str)
    
    def execute_query(self) -> pd.DataFrame:
        """
        Execute the query to get the data

        Returns:
            pd.DataFrame: DeltaV dataframe
        """
        if 'last_processed_timestamp' not in self.state :
            self.state['last_processed_timestamp'] = pytz.utc.localize(datetime.utcnow(), is_dst=None)\
                                                        .astimezone(self.tz).strftime("%Y-%m-%d %X")
        last_processed_timestamp = self.state['last_processed_timestamp']
        query = f"""
            SELECT 
                t4.actualState, 
                t4.occurTime,
                t4.userName, 
                t4.userComment, 
                t3.* 
            FROM (SELECT t2.description AS recipe, 
                t1.unitprocedure, 
                t1.operation,
                t1.phase, 
                t1.unit, 
                t1.uniqueid, 
                t1.starttime, 
                t1.endtime, 
                t1.actionType, 
                t1.processcell, 
                t1.area 
                FROM batchrecipeview AS t1 
                LEFT JOIN batchview AS t2 
                ON t1.uniqueid = t2.uniqueid) t3 
            LEFT JOIN BRecipeStateChangeEvent t4 
            ON t4.actionKeyName = '\\\\\\'+t3.unitprocedure+'\\'+t3.operation+'\\'+t3.phase+'\\' and t4.uniqueBatchId = t3.uniqueid 
            WHERE t3.endtime >= '{last_processed_timestamp}'
        """
        return pd.read_sql(query, self.get_connection())     

    def start(self) -> None:
        """
        Start the connector
        """
        self.tz = pytz.timezone(self.connector_config.db_timezone)
        self.start_kafka_worker()  # Start Kafka worker
        while(self._running):
            try:
                self.process_records(self.execute_query())
                time.sleep(self.connector_config.query_frequency)
            except Exception as e:
                self.logger.exception(f"Error processing records: {e}", exc_info=True)
                self.stop_kafka_worker()
                self.close()
                self.logger.info("DeltaVSource closed")
    
    def test_config(self):
        try:
            conn = self.get_connection()
            conn.close()
            return "Connection successful"
        except Exception as e:
            return f"Failed to get connection: {e}"
            

