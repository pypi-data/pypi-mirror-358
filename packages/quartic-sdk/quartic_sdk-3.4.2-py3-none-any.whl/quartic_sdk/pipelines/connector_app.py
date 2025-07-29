import logging
import os
import sys
import cloudpickle
import base64
import marshal
from typing import final
from quartic_sdk.model.helpers import ModelUtils
from typing import Callable, Optional
from abc import ABC, abstractmethod
from enum import Enum
from quartic_sdk import GraphqlClient
from quartic_sdk.utilities.kafka import KafkaBatchConsumer
from quartic_sdk.pipelines.settings import settings

MAX_CONNECTOR_PKL_SIZE = 10 * 1024 * 1024  # 10 MB
class BaseConfig:
    def dict(self):
        return self.__dict__
    
class AppConfig(BaseConfig):
    def __init__(self,
    kafka_partition: str = '3',
    executor_core_request: str = '500m',
    driver_core_request: str = '500m',
    driver_memory_request: str = '500m',
    executor_memory_request: str = '500m',
    executor_instance: str = '1',
    requirements: dict = {}):
            
        self.kafka_partition: str = kafka_partition
        self.executor_core_request: str = executor_core_request
        self.driver_core_request: str = driver_core_request
        self.driver_memory_request: str = driver_memory_request
        self.executor_memory_request: str = executor_memory_request
        self.executor_instance: str = executor_instance
        self.requirements: dict = requirements
    

class CONNECTOR_CLASS(Enum):
    Http = "HTTP"
    HttpSoap = "HTTP_SOAP"
    EventHub = "AZURE_EVENT_HUB"
    External = "EXTERNAL"
    Custom = "CUSTOM_PYTHON"
    DeltaV = 'DELTA_V_SQL'
    Opcua = 'OPCUA'
    Telemetry_Internal = 'TELEMETRY_INTERNAL'
    Batch_Internal = 'BATCH_INTERNAL'
    ModelMapping = 'MODEL_MAPPING'


GET_CONNECTORS_QUERY = """
query MyQuery($ids: [String!]) {
  ConnectorApp(id_In: $ids) {
    id
    name
    connectorClass
  }
}
"""

STATE_BASE_DIR = settings.internal_sink_state_directory

class ConnectorApp(ABC):
    '''
    Abstract Base class for all connectors
    connector_config is nullable for external connectors
    transformation and connector_config is stored in the pickle and not in the database
    '''

    WAIT_BEFOßECONDS = 5
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', "")
        self.source = kwargs.get('source', [])
        self.transformation = kwargs.get('transformation', None)
        self.app_config = kwargs.get('app_config', AppConfig())
        self.topic_to_push: str = kwargs.get('topic_to_push', None)
        self.connector_config = kwargs.get('connector_config', None)
        self.gql_client = kwargs.get('gql_client', None)
        self.test_run = kwargs.get('test_run', False)
        self.accessible_groups = kwargs.get('accessible_groups', [])
        self._logger: Optional[logging.Logger] = None
        self._running = True
        self.state = self.__get_state()
        
    def __get_state_pickle_file(self):
        if not os.path.exists(STATE_BASE_DIR):
            self.logger.info(f"Creating state dir {STATE_BASE_DIR}")
            os.system(f"mkdir -p {STATE_BASE_DIR}")

        return f"{STATE_BASE_DIR}/state_{self.id}.pkl"

    def __get_state(self):
        filename = self.__get_state_pickle_file()
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return cloudpickle.load(f) or {}
        return {}

    def __write_state(self, state: dict):
        filename = self.__get_state_pickle_file()
        self.logger.info(f"Writing state to {filename}")
        with open(filename, "wb") as f:
            cloudpickle.dump(state, f)
    
    def close(self):
        self.logger.info("Closing ConnectorApp")
        self._running = False
        self.__write_state(self.state)


    @abstractmethod
    def start(self, 
              id: int,
              kafka_topics: list[str],
              source: Optional[list[int]] = None):
        raise NotImplementedError


    def save_with_pickle(self):
        connector_pkl = ModelUtils.get_pickled_object(self)
        assert sys.getsizeof(connector_pkl) <= MAX_CONNECTOR_PKL_SIZE, \
            f"Connector pickle size can't be more than {MAX_CONNECTOR_PKL_SIZE} MB"
        variables = {
            'name': self.name,
            'sourceConnectors': self.source,
            'connectorType': self.connector_type,
            'appConfig': self.app_config.dict(),
            'model': connector_pkl,
            'connectorClass': self.connector_class,
            'accessibleGroups': self.accessible_groups
        }
        mutation_call = 'ConnectorappCreate'
        
        MUTATION = """
            mutation createupdateConnector(
                $name: String!,
                $sourceConnectors: [ID],
                $connectorType: ConnectorAppConnectorTypeEnumCreate!,
                $appConfig: CustomDict!,
                $model: String!,
                $connectorClass: ConnectorAppConnectorClassEnumCreate!,
                $accessibleGroups: [ID!]
            ) {
                ConnectorappCreate(
                    newConnectorapp: {
                        name: $name,
                        sourceConnectors: $sourceConnectors,
                        connectorType: $connectorType,
                        appConfig: $appConfig,
                        model: $model,
                        connectorClass: $connectorClass,
                        accessibleGroups: $accessibleGroups
                    }) 
                {
                    connectorapp {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        UPDATE_MUTATION = """
        mutation createupdateConnector(
  							$id:ID!,
                $name: String!,
                $sourceConnectors: [ID],
                $connectorType: ConnectorAppConnectorTypeEnumCreate!,
                $appConfig: CustomDict!,
                $model: String!,
                $connectorClass: ConnectorAppConnectorClassEnumCreate!,
                $accessibleGroups: [ID!]
            ) {
                ConnectorappUpdate(
                    updateConnectorapp: {
                      	id:$id,
                        name: $name,
                        sourceConnectors: $sourceConnectors,
                        connectorType: $connectorType,
                        appConfig: $appConfig,
                        model: $model,
                        connectorClass: $connectorClass,
                        accessibleGroups: $accessibleGroups
                    })
                {
                    connectorapp {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        if self.id:
            variables['id'] = self.id
            mutation_call = 'ConnectorappUpdate'
            MUTATION = UPDATE_MUTATION
        print("Saving the Connector to Quartic Platform")
        response = self.gql_client.execute_query(MUTATION, variables)
        if not response['data'][mutation_call]['ok']:
            raise Exception(response['data'][mutation_call]['errors'])
        
        self.id = int(response['data'][mutation_call]['connectorapp']['id'])
        print(response)

        print("Successfully saved the Connector to Quartic Platform")
        return response


    def save_function_to_string(self):
        code_bytes = marshal.dumps(self.transformation.__code__)
        base64_string = base64.b64encode(code_bytes).decode("utf-8")
        return base64_string


    @final
    def save(self):
        connector_config = {}
        if self.connector_config:
            for k, v in self.connector_config.dict().items():
                if v is not None:
                    connector_config[k] = v
        if self.transformation:
            connector_config['transformation'] = self.save_function_to_string()
        variables = {
            'name': self.name,
            'sourceConnectors': self.source,
            'connectorType': self.connector_type,
            'appConfig': self.app_config.dict(),
            'connectorConfig': connector_config,
            'connectorClass': self.connector_class,
            'accessibleGroups': self.accessible_groups
        }
        mutation_call = 'ConnectorappCreate'

        MUTATION = """
            mutation createupdateConnector(
                $name: String!,
                $sourceConnectors: [ID],
                $connectorType: ConnectorAppConnectorTypeEnumCreate!,
                $appConfig: CustomDict!,
                $connectorConfig: CustomDict!,
                $connectorClass: ConnectorAppConnectorClassEnumCreate!,
                $accessibleGroups: [ID!]
            ) {
                ConnectorappCreate(
                    newConnectorapp: {
                        name: $name,
                        sourceConnectors: $sourceConnectors,
                        connectorType: $connectorType,
                        appConfig: $appConfig,
                        connectorConfig: $connectorConfig,
                        connectorClass: $connectorClass,
                        accessibleGroups: $accessibleGroups
                    }) 
                {
                    connectorapp {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        UPDATE_MUTATION = """
        mutation createupdateConnector(
  							$id:ID!,
                $name: String!,
                $sourceConnectors: [ID],
                $connectorType: String!,
                $appConfig: CustomDict!,
                $connectorConfig: CustomDict!,
                $connectorClass: String!,
                $accessibleGroups: [ID!]
            ) {
                ConnectorappUpdate(
                    updateConnectorapp: {
                      	id:$id,
                        name: $name,
                        sourceConnectors: $sourceConnectors,
                        connectorType: $connectorType,
                        appConfig: $appConfig,
                        connectorConfig: $connectorConfig,
                        connectorClass: $connectorClass,
                        accessibleGroups: $accessibleGroups
                    })
                {
                    connectorapp {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        if self.id:
            variables['id'] = self.id
            mutation_call = 'ConnectorappUpdate'
            MUTATION = UPDATE_MUTATION
        print("Saving the Connector to Quartic Platform")
        response = self.gql_client.execute_query(MUTATION, variables)
        if not response['data'][mutation_call]['ok']:
            raise Exception(response['data'][mutation_call]['errors'])
        
        self.id = int(response['data'][mutation_call]['connectorapp']['id'])
        print(response)

        print("Successfully saved the Connector to Quartic Platform")
        return response
    
    def delete(self):
        MUTATION = """
            mutation deleteConnector($id: ID!) {
            ConnectorappDelete(id: $id) {
                errors {
                messages
                field
                }
                ok
            }
            }
        """
        response = self.gql_client.execute_query(MUTATION, {'id': self.id})
        if not response['data']['ConnectorappDelete']['ok']:
            raise Exception(response['data']['ConnectorappDelete'])
        print("Successfully deleted the Connector")

    @final
    def deploy(self):
        
        variables = {
            'id': self.id
        }
        DEPLOY_CONNECTOR_QUERY = """
        query deployConnector($id: Int!) {
            deployConnector(connectorId: $id) 
        }
        """
        response = self.gql_client.execute_query(DEPLOY_CONNECTOR_QUERY, variables)
        if not response['data']['deployConnector']['status'] == 200:
            raise Exception(response['data']['deployConnector']['status'])
        print("Successfully deployed the Connector to Quartic Platform")

    @staticmethod
    def get_connector(client, connector_id: int):
        '''
        Get connectcor from QPro
        '''

        GET_CONNECTORS_QUERY = """
            query getConnectors($id: Float!){
            ConnectorApp(id: $id) {
                createdAt
                connectorType
                appConfig
                id
                isDeployed
                connectorClass
                connectorConfig
                updatedAt
                sourceConnectors {
                id
                name
                isDeployed
                }
            }
            }
        """
        connector_resp = client.execute_query(GET_CONNECTORS_QUERY, {'id' : connector_id})
        connector_data = connector_resp['data']['ConnectorApp'][0]
        if connector_data['modelStr']:  
            connector =  cloudpickle.loads(base64.b64decode(connector_data['modelStr']))
            connector.id = int(connector_data['id'])
            return connector
        return connector_data


    @property
    def logger(self):
        if not getattr(self, "_logger", None):
            self._logger = logging.getLogger(f"{self.__class__.__name__}:{self.id}")
            self.configure_logger(self._logger)
        return self._logger

    def configure_logger(self, logger: logging.Logger):
        """Called first time after a logger is created"""
        logger.setLevel(logging.INFO)

    def get_source_map(self, client: GraphqlClient):
        response = client.execute_query(
            GET_CONNECTORS_QUERY,
            {"ids": [str(s) for s in self.source]},
        )
        self.source_map = {}
        for connector in response["data"]["ConnectorApp"]:
            self.source_map[connector["id"]] = connector["connectorClass"]
        self.logger.info(f"Loaded source map {self.source_map}")
        return self.source_map

    def get_kafka_consumer(self, kafka_topics: list[str]):
        if hasattr(self, "sink_topic"):
            self.sink_topic = next(
                filter(lambda t: t.split("_")[1] == str(self.id), kafka_topics), None
            )
        source_topics = [t for t in kafka_topics if t != self.sink_topic]
        consumer = KafkaBatchConsumer(
            conf={
                **settings.get_kafka_config(),
                "group.id": f"source_{self.id}",
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                "receive.message.max.bytes": 2000000000,
            },
            topics=source_topics,
        )
        return consumer


class ExternalApp(ConnectorApp):
    """Generic external connector application implementation"""
    connector_class = CONNECTOR_CLASS.External.value
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_type = kwargs.get('connector_type', 'SOURCE_AND_SINK')

    @final
    def start(self, *args, **kwargs):
        raise NotImplementedError("Can't start external connectors")
    
    @final
    def deploy(self, client):
        raise NotImplementedError("Can't deploy external connectors")


def get_truststore_password() -> str:
    """
    Read Kafka SSL truststore password from file

    Returns:
        str: password
    """
    import os
    truststore_path = os.getenv('KAFKA_SSL_TRUSTSTORE_PASSWORD',"")
    if not truststore_path:
        return truststore_path
    with open(truststore_path, 'r') as file:
        password = file.read().strip()
    return password
