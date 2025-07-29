from abc import ABC
from datetime import datetime

from pydantic import BaseModel
from typing import Literal, Optional, Any, Callable


class InternalOperation(BaseModel):
    optype: str


# Tags


class TagCreate(InternalOperation):
    optype = "TAG_CREATE"
    name: str
    edge_connector: int
    tag_type: str


class TagUpdate(TagCreate):
    optype = "TAG_UPDATE"
    id: int


class TagDelete(InternalOperation):
    optype = "TAG_DELETE"
    id: int


# Telemetry


class TagTelemetry(InternalOperation):
    optype = "TAG_TELEMETRY"
    timestamp: int
    edgeconnector: int
    tag: str
    value: Any

class BatchDelta(InternalOperation):
    optype = "BATCH_DELTA"
    recipe: str
    unitprocedure: str
    operation: str
    phase: str
    uniqueid: str
    starttime: int
    endtime: int
    unit: str
    
# Asset


class AssetCreate(InternalOperation):
    optype = "ASSET_CREATE"
    name: str
    entity: int
    last_overhaul_date: int
    tags: list[int]


class AssetDelete(InternalOperation):
    optype = "ASSET_DELETE"
    id: int


class AssetUpdate(InternalOperation):
    optype = "ASSET_UPDATE"
    id: int
    entity: int
    last_overhaul_date: int
    tags: list[int]


# Batches


class ProcedureStepBatchCreate(InternalOperation):
    optype = "PROCEDURE_STEP_BATCH_CREATE"
    batch_name: str
    batch_type: str
    procedure_step_component: int
    sequential: bool
    start_time: int
    stop_time: Optional[int]


class ProcedureStepBatchDelete(InternalOperation):
    optype = "PROCEDURE_STEP_BATCH_DELETE"
    id: int


class ProcedureStepBatchUpdate(ProcedureStepBatchCreate):
    optype = "PROCEDURE_STEP_BATCH_UPDATE"
    id: int


# GraphQL


class GQLQuery(InternalOperation):
    """
    Generic operation to run arbitrary GQL queries/mutations
        query:
            GQL query to execute
        variables:
            Dictionary of gql variable definitions
        is_ok:
            Optionally specify a callable that checks the operation response
            and returns true if the operation succeeded.
    """

    optype = "GQL_QUERY"
    query: str
    variables: dict
    is_ok: Optional[Callable[[Optional[dict]], bool]]
