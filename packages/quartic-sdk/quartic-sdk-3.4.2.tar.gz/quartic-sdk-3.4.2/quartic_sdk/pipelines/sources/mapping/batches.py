import copy
import logging

import pandas as pd

from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.sources.mapping.base import MappingProcessor

logger = logging.getLogger(__name__)

BATCHES = "BATCHES"
OPERATION = "operation"
UNITPROCEDURE = "unitprocedure"
UNIQUE_ID = "uniqueid"
PHASE = "phase"


class BatchMappingProcessor(MappingProcessor):
    @classmethod
    def get_source_classes(cls):
        return [
            CONNECTOR_CLASS.DeltaV.value,
        ]

    def process(self, df: pd.DataFrame, connector_id: int):
        state = self.get_state(connector_id)
        batches = state.setdefault(BATCHES, {})

        res = []
        for _, row in df.iterrows():
            try:
                uniqueid = row[UNIQUE_ID]
                batch = batches.setdefault(
                    uniqueid,
                    {
                        "recipe": row.get("recipe", None),
                        "uniqueid": uniqueid,
                        "area": row.get("area", None),
                        "processcell": row.get("processcell", None),
                        "unit": row.get("unit", None),
                        "phasemodule": row.get("phasemodule", None),
                        "batchID": row.get("batchID", None),
                    },
                )
                operation = row.get(OPERATION, None) or None
                phase = row.get(PHASE, None) or None
                if operation and phase:
                    self._map_phase(batch, row)
                elif operation:
                    self._map_operation(batch, row)
                else:
                    self._map_unitprocedure(batch, row)

                copy.deepcopy(batch)
                res.append((uniqueid, batch))
            except Exception:
                logger.exception(f"Error while processing row {row}")

        self.write_state(state, connector_id)
        return res

    def _map_phase(self, batch: dict, row: pd.Series):
        # Resolve unit procedure
        unitprocedure = batch.get(UNITPROCEDURE, {})
        up_name = row[UNITPROCEDURE]
        if unitprocedure and unitprocedure['name'] != up_name:
            logger.info(f"Received phase before UP {up_name}")

        # Resolve operation
        operation = batch.get(OPERATION, {})
        op_name = row[OPERATION]
        if operation and operation['name'] != up_name:
            logger.info(f"Received phase before OP {op_name}")

        # Resolve phase
        phase_name = row[PHASE]
        new, phase = self.__get_or_create_phase(phase_name, batch)
        if not new:
            logger.info(f"Phase {phase_name} already exists.")
        self.__map_object(self.__to_common_dict(row, PHASE), phase)

    def _map_operation(self, batch: dict, row: pd.Series):
        # Resolve unit procedure
        unitprocedure = batch.get(UNITPROCEDURE, {})
        up_name = row[UNITPROCEDURE]
        if unitprocedure and unitprocedure['name'] != up_name:
            logger.info(f"Received operation before UP {up_name}")

        # Resolve operation
        op_name = row[OPERATION]
        new, operation = self.__get_or_create_op(op_name, batch)
        if new:
            batch[PHASE] = self.__get_default_dict("")
        else:
            logger.info(f"Operation {op_name} already exists")
        self.__map_object(self.__to_common_dict(row, OPERATION), operation)

    def _map_unitprocedure(self, batch: dict, row: pd.Series):
        # Resolve unit procedure
        up_name = row[UNITPROCEDURE]
        new, unitprocedure = self.__get_or_create_up(up_name, batch)
        if new:
            batch[OPERATION] = self.__get_default_dict("")
            batch[PHASE] = self.__get_default_dict("")
        else:
            logger.info(f"Unitprocedure {up_name} already exists")
        self.__map_object(self.__to_common_dict(row, UNITPROCEDURE), unitprocedure)

    def __get_or_create_up(self, up_name: str, batch: dict):
        unitprocedure = batch.setdefault(UNITPROCEDURE, {})
        new = False
        if not unitprocedure or unitprocedure['name'] != up_name:
            new = True
            unitprocedure = self.__get_default_dict(up_name)
        return new, unitprocedure

    def __get_or_create_op(self, op_name: str, batch: dict):
        operation = batch.setdefault(OPERATION, {})
        new = False
        if not operation:
            new = True
            operation = self.__get_default_dict(op_name)
        return new, operation

    def __get_or_create_phase(self, phase_name: str, batch: dict):
        phase = batch.setdefault(PHASE, {})
        new = False
        if not phase:
            new = True
            phase = self.__get_default_dict(phase_name)
        return new, phase

    def __map_object(self, source: dict, target: dict):
        for k, v in source.items():
            if not v and k in target:
                logger.info(
                    f"Ignoring source key {k}. Key already present in target: {target[k]}"
                )
                continue
            target[k] = v

    def __to_common_dict(self, row: pd.Series, name_key: str):
        return {
            "name": row[name_key],
            "starttime": row["starttime"],
            "endtime": row["endtime"],
            "userName": row["userName"],
            "userComment": row["userComment"],
            "actualState": row["actualState"]
        }
    
    def __get_default_dict(self, name: str):
        return {
            "name": name,
            "starttime": None,
            "endtime": None,
            "userName": "",
            "userComment": "",
            "actualState": ""
        }
