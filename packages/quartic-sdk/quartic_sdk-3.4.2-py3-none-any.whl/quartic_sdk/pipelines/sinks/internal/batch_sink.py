from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.sinks.base_sink import KafkaSinkApp
from quartic_sdk.pipelines.connector_app import BaseConfig
import os
import json
from quartic_sdk import GraphqlClient
from pydantic import BaseModel
import pandas as pd
import time


class BatchSinkConfig(BaseModel, BaseConfig):
    site_id: int
    product_id: int


class BatchSink(KafkaSinkApp):
    """
    Batch Internal Sink application.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_class: str = CONNECTOR_CLASS.Batch_Internal.value
        self.connector_config: BatchSinkConfig = kwargs.get("connector_config")
        self.gql_client = GraphqlClient.get_graphql_client_from_env()
    
    def get_asset_id(self,  asset_name: str) -> int:
        """Get asset id

        Args:
            asset_name (str): Asset name

        Returns:
            int: Asset id
        """
        query = """
            query MyQuery($name: String) {
                Asset(name_Iexact: $name) {
                    id
                    name
                }
            }
        """
        variables = {
            "name": asset_name
        }
        response = self.gql_client.execute_query(query, variables)
        return response['data']['Asset'][0]['id']
    
    def get_procedure_hierarchy(self) -> dict:
        """Get procedure hierarchy

        Returns:
            dict: Procedure hierarchy
        """
        query = """
            query MyQuery($product_id : ID, $procedure_state: String) {
                Procedure(procedureState: $procedure_state, product: $product_id) {
                    id
                    procedureStepNodes {
                    stepComponents {
                        id
                    }
                    id
                    name
                    stepType
                    parent {
                        name
                    }
                    procedure{
                        name
                      id
                    }
                    }
                    name
                }    
            }
        """
        active_procedure_state = "4"    
        variables = {
            "procedure_state": active_procedure_state,
            "product_id" : str(self.connector_config.product_id)
        }
        response = self.gql_client.execute_query(query, variables)
        if not response['data']['Procedure']:
            return {}

        return self.get_hierarchy(response)

    def get_hierarchy(self, data: dict):
        """Get procedure hierarchy

        Args:
            data (dict): Procedure data

        Returns:
            dict: Procedure hierarchy
        """
        hierarchy = {}
        for procedure_data in data['data']['Procedure']:
            procedure_id = procedure_data['id']
            
            for item in procedure_data["procedureStepNodes"]:
                if not item['parent']:
                    hierarchy[item['name']] = {}
                    hierarchy[item['name']]['id'] = procedure_id
                    hierarchy[item['name']]['step_component_id'] = item['stepComponents'][0]['id']
                    hierarchy[item['name']]['step_id'] = item['id']
                else:
                    for procedure in hierarchy:
                        if procedure == item['parent']['name'] and procedure == item['procedure']['name']:
                            hierarchy[procedure][item['name']] = {}
                            hierarchy[procedure][item['name']]['id'] = item['id']
                            hierarchy[procedure][item['name']]['step_component_id'] = item['stepComponents'][0]['id']
                            break
                        for up in hierarchy[procedure]:
                            if up == item['parent']['name'] and procedure == item['procedure']['name']:
                                hierarchy[procedure][up][item['name']] = {}
                                hierarchy[procedure][up][item['name']]['id'] = item['id']
                                hierarchy[procedure][up][item['name']]['step_component_id'] = item['stepComponents'][0]['id']
                                break
                            for op in hierarchy[procedure][up] :
                                if op == item['parent']['name'] and procedure == item['procedure']['name']:
                                    hierarchy[procedure][up][op][item['name']] = {}
                                    hierarchy[procedure][up][op][item['name']]['id'] = item['id']
                                    hierarchy[procedure][up][op][item['name']]['step_component_id'] = item['stepComponents'][0]['id']
                                    break
        return hierarchy

    def update_step_component(self, id: int, asset_id: int):
        """Update a step component

        Args:
            id (int): Step component id
            asset_id (int): Asset id
        """
        ur_variables = {
            "id": id,
            "asset": asset_id
        }
        ur_query = """mutation UpdateStepComponent($id: ID!, $asset: ID!) {
            ProcedurestepcomponentUpdate(
                updateProcedurestepcomponent: {id: $id, asset: $asset}
            ) {
                ok
                errors {
                field
                messages
                __typename
                }
                procedurestepcomponent {
                id
                __typename
                }
                __typename
            }
            }"""
        data = self.gql_client.execute_query(ur_query, ur_variables)

        return data['data']['ProcedurestepcomponentUpdate']['procedurestepcomponent']
    
    def create_recipe(self, name: str):
        """Create a recipe

        Args:
            name (str): Recipe name
        """
        recipe_query = """mutation RecipeCreate($site: ID!, $name: String!, $product: ID!, $procedureType: ProcedureProcedureTypeEnumCreate, $procedureState: ProcedureProcedureStateEnumCreate) {
            ProcedureCreate(
            newProcedure: {name: $name, product: $product, site: $site, procedureType: $procedureType, procedureState: $procedureState}
            ) {
            procedure {
                id
                name
                procedureType
                procedureStepNodes{
                    id
                    stepComponents{
                        id
                    }
                }
                __typename
            }
            ok
            errors {
                messages
                field
                __typename
            }
            __typename
            }
        }"""
        recipe_variables = {
            "name": name,
            "site": self.connector_config.site_id,
            "procedureType": "A_2",
            "product": str(self.connector_config.product_id),
            "procedureState": "A_4"
            }
        data = self.gql_client.execute_query(recipe_query, recipe_variables)
        return data['data']['ProcedureCreate']['procedure']
    
    
    def create_procedure_step(self, name: str, order: int, procedure: int, parent: int, step_type: str):
        """Create a procedure step

        Args:
            name (str): Step name
            order (int): Step order
            procedure (int): Procedure id
            parent (int): Parent id
            step_type (str): Step type
        """
        up_query = """mutation CreateProcedureStep($name: String!, $order: Int!, $parent: ID, $stepComponents: [ID!]!, $stepType: ProcedureStepStepTypeEnumCreate!, $procedure: ID!) {
            ProcedurestepCreate(
                newProcedurestep: {name: $name, order: $order, stepComponents: $stepComponents, stepType: $stepType, parent: $parent, procedure: $procedure}
            ) {
                ok
                procedurestep {
                id
                name
                order
                stepType
                stepComponents{
                        id
                }
                __typename
                }
                ok
                errors {
                messages
                field
                __typename
                }
                __typename
            }
            }"""
        up_variables = {
            "name": name,
            "stepType": step_type,
            "procedure": procedure,
            "order": order,
            "stepComponents": [],
            "parent": parent
        }
        data = self.gql_client.execute_query(up_query, up_variables)
        self.logger.info(f"Created procedure step {name} with id {data['data']['ProcedurestepCreate']['procedurestep']['id']}")
        return data['data']['ProcedurestepCreate']['procedurestep']
    
    
    def create_valid_entries(self, hierarchy: dict, asset: int):
        """Create valid entries in hierarchy

        Args:
            hierarchy (dict): Procedure hierarchy
            asset (int): Asset id
        """
        for procedure in hierarchy:
            if not procedure:
                self.logger.error(f"Unexpected empty procedure in hierarchy ({procedure})")
                continue
            if 'id' not in hierarchy[procedure]:
                resp = self.create_recipe(procedure)
                hierarchy[procedure]['id'] = resp['id']
                hierarchy[procedure]['step_component_id'] = resp['procedureStepNodes'][0]['stepComponents'][0]['id']
                hierarchy[procedure]['step_id'] = resp['procedureStepNodes'][0]['id']
            up_order = 1
            for up in hierarchy[procedure]:
                if up in ['id', 'step_component_id', 'step_id']:
                    continue
                if 'id' not in hierarchy[procedure][up]:
                    resp = self.create_procedure_step(up, up_order, hierarchy[procedure]['id'], hierarchy[procedure]['step_id'], "A_1")
                    hierarchy[procedure][up]['id'] = resp['id']
                    hierarchy[procedure][up]['step_component_id'] = resp['stepComponents'][0]['id']
                op_order = 1
                for op in hierarchy[procedure][up]:
                    if op in ['id', 'step_component_id']:
                        continue
                    if 'id' not in hierarchy[procedure][up][op]:
                        resp = self.create_procedure_step(op, op_order, hierarchy[procedure]['id'], hierarchy[procedure][up]['id'], "A_2")
                        hierarchy[procedure][up][op]['id'] = resp['id']
                        hierarchy[procedure][up][op]['step_component_id'] = resp['stepComponents'][0]['id']
                        self.update_step_component(hierarchy[procedure][up][op]['step_component_id'], asset)
                    phase_order = 1
                    for phase in hierarchy[procedure][up][op]:
                        if phase in ['id', 'step_component_id']:
                            continue
                        if 'id' not in hierarchy[procedure][up][op][phase]:
                            resp = self.create_procedure_step(phase, phase_order, hierarchy[procedure]['id'], hierarchy[procedure][up][op]['id'], "A_3")
                            hierarchy[procedure][up][op][phase]['id'] = resp['id']
                            hierarchy[procedure][up][op][phase]['step_component_id'] = resp['stepComponents'][0]['id']
                        phase_order+= 1
                    op_order += 1
                up_order += 1
    
    def create_procedure_batch(self, batch: str, start: int, stop: int, stepcomponent: str, batch_type: str):
        """Create a batch

        Args:
            batch (str): Batch name
            start (int): Start time
            stop (int): Stop time
            stepcomponent (str): Step component id
            batch_type (str): Batch type
        """
        query = """mutation MyMutation($batchName: String!, $batchType: String!, $procedureStepComponent: String!, $sequential: Boolean!, $startTime: CustomDateTime!, $stopTime: CustomDateTime, ) {
            __typename
            createOrUpdateBatch(batchName: $batchName, batchType: $batchType, procedureStepComponent: $procedureStepComponent, sequential: $sequential, startTime: $startTime, stopTime: $stopTime) {
                status
                message
            }
            }"""
        variables = {
            "batchName": batch,
            "startTime":  start,
            "stopTime": stop,
            "procedureStepComponent": stepcomponent,
            "sequential": True,
            "batchType": batch_type
        }
        data = self.gql_client.execute_query(query, variables)
        self.logger.info(f"Created batch {batch} with status {data['data']['createOrUpdateBatch']['status']}")
    
    def handle(self, data: pd.DataFrame) -> None:
        """Build procedure hierarchy and create batches

        Args:
            data (pd.DataFrame): DataFrame containing records from Kafka
        """
        
        procedure_hierarchy = self.get_procedure_hierarchy()
        for index, row in data.iterrows():
            creation_needed = False
            if row['recipe'] not in procedure_hierarchy:
                procedure_hierarchy[row['recipe']] = {}
                creation_needed = True
            if not pd.isna(row['unitprocedure']) and row['unitprocedure'] != '' and row['unitprocedure'] not in procedure_hierarchy[row['recipe']]:
                procedure_hierarchy[row['recipe']][row['unitprocedure']] = {}
                creation_needed = True
            if not pd.isna(row['operation']) and row['operation'] != '' and row['operation'] not in procedure_hierarchy[row['recipe']][row['unitprocedure']]:
                procedure_hierarchy[row['recipe']][row['unitprocedure']][row['operation']] = {}
                creation_needed = True
            if not pd.isna(row['phase']) and row['phase'] != '' and row['phase'] not in procedure_hierarchy[row['recipe']][row['unitprocedure']][row['operation']]:
                procedure_hierarchy[row['recipe']][row['unitprocedure']][row['operation']][row['phase']] = {}
                creation_needed = True
            if creation_needed:
                self.create_valid_entries(procedure_hierarchy, row['unit'])
                  
            if row['endtime'] > int(time.time()*1000):
                batch_type = '0'
                row['endtime'] = None

            else:
                batch_type = '2'
            if not pd.isna(row['phase']) and row['phase'] != '':
                step_comp = procedure_hierarchy[row['recipe']][row['unitprocedure']][row['operation']][row['phase']]['step_component_id']
                self.create_procedure_batch(row['uniqueid'], row['starttime'], row['endtime'], step_comp, batch_type)
            elif not pd.isna(row['operation']) and row['operation'] != '':
                step_comp = procedure_hierarchy[row['recipe']][row['unitprocedure']][row['operation']]['step_component_id']
                self.create_procedure_batch(row['uniqueid'], row['starttime'], row['endtime'], step_comp, batch_type)
            elif not pd.isna(row['unitprocedure']) and row['unitprocedure'] != '':
                step_comp = procedure_hierarchy[row['recipe']][row['unitprocedure']]['step_component_id']
                self.create_procedure_batch(row['uniqueid'], row['starttime'], row['endtime'], step_comp, batch_type)
                self.create_procedure_batch(row['uniqueid'], row['starttime'], row['endtime'], procedure_hierarchy[row['recipe']]['step_component_id'], batch_type)

            elif not pd.isna(row['recipe']) and row['recipe'] != '':
                step_comp = procedure_hierarchy[row['recipe']]['step_component_id']
                self.create_procedure_batch(row['uniqueid'], row['starttime'], row['endtime'], step_comp, batch_type)
    
    def get_df_to_process(self, df: pd.DataFrame):
        """Filter DataFrame to only include records for assets that is already in platform

        Args:
            df (pd.DataFrame): DataFrame containing records from Kafka

        Returns:
            pd.DataFrame: DataFrame containing records to process
        """
        unique_units = df['unit'].unique()
        df_to_process = pd.DataFrame()
        for unit in unique_units:
            if unit in self.state['asset_mapping']:
                unit_id = self.state['asset_mapping'][unit]
            else:
                try:
                    unit_id = self.get_asset_id(unit)
                    self.state['asset_mapping'][unit] = unit_id
                except Exception as e:
                    self.logger.error(f'Error getting asset id for {unit}: {e}')
            df_to_process = pd.concat([df_to_process, df[df['unit'] == unit]])
            df_to_process['unit'] = df_to_process['unit'].apply(lambda x: unit_id if x == unit else x)
        return df_to_process
    
    def process_records(self, data: pd.DataFrame):
        """Process records from Kafka

        Args:
            data (pd.DataFrame): DataFrame containing records from Kafka
        """
        values = data.value.apply(json.loads).to_list()
        #convert to dataframe
        values_df = pd.DataFrame(values)
        self.logger.info(f"Processing {len(values_df)} records")
        if 'asset_mapping' not in self.state:
            self.state['asset_mapping'] = {}
        df_to_process = self.get_df_to_process(values_df)
        self.handle(df_to_process)
        self.logger.info(f"Processed {len(values_df)} records successfully")
    
    def test_config(self):
        try:
            query = """query MyQuery($product_id: Float, $site_id: Float) {
                Product(id: $product_id) {
                    id
                    name
                }
                Site(id: $site_id) {
                    id
                    name
                }
            }"""
            variables = {
                "product_id": self.connector_config.product_id,
                "site_id": self.connector_config.site_id
            }
            data = self.gql_client.execute_query(query, variables)
            if len(data['data']['Product']) == 0:
                raise Exception("Product not found")
            if len(data['data']['Site']) == 0:
                raise Exception("Site not found")
            return "Connection successful"
        except Exception as e:
            return f"Failed to write data: {e}"
