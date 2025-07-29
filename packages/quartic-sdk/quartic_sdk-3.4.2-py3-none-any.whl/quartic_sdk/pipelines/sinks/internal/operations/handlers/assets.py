import logging

from quartic_sdk.pipelines.sinks.internal.operations.handlers.base import (
    GQLOperationHandler,
)
from quartic_sdk.pipelines.sinks.internal.operations.operations import (
    AssetCreate,
    AssetDelete,
    AssetUpdate,
)

logger = logging.getLogger(__name__)


ASSET_CREATE_MUTATION = """
mutation createAsset(
    $entity: ID!,
    $name: String!,
    $lastOverhaulDate: CustomDateTime!,
    $tags: [ID]
) {
    AssetCreate(newAsset: {
        entity: $entity,
        lastOverhaulDate: $lastOverhaulDate,
        name: $name,
        tags: $tags
    }) {
        ok
        errors {
            field
            messages
        }
    }
}
"""
ASSET_DELETE_MUTATION = """
mutation deleteAsset($id: ID!) {
    AssetDelete(id: $id) {
        ok
        errors {
            field
            messages
        }
    }
}
"""
ASSET_UPDATE_MUTATION = """
mutation updateAsset(
    $id: ID!,
    $entity: ID!,
    $lastOverhaulDate: CustomDateTime!,
    $tags: [ID]
) {
    AssetUpdate(
        updateAsset: {
            id: $id,
            entity: $entity,
            lastOverhaulDate: $lastOverhaulDate,
            tags: $tags
        }
    ) {
        ok
        errors {
            field
            messages
        }
    }
}
"""


class AssetCreateHandler(GQLOperationHandler[AssetCreate]):
    @classmethod
    def get_optype(cls):
        return AssetCreate

    def get_success_field(self):
        return "data.AssetCreate.ok"

    def get_query(self, op: AssetCreate):
        return ASSET_CREATE_MUTATION, {
            "name": op.name,
            "entity": op.entity,
            "lastOverhaulDate": op.last_overhaul_date,
            "tags": op.tags,
        }


class AssetDeleteHandler(GQLOperationHandler[AssetDelete]):
    @classmethod
    def get_optype(cls):
        return AssetDelete

    def get_success_field(self):
        return "data.AssetDelete.ok"

    def get_query(self, op: AssetDelete):
        return ASSET_DELETE_MUTATION, {"id": op.id}


class AssetUpdateHandler(GQLOperationHandler[AssetUpdate]):
    @classmethod
    def get_optype(cls):
        return AssetUpdate

    def get_success_field(self):
        return "data.AssetUpdate.ok"

    def get_query(self, op: AssetUpdate):
        return ASSET_UPDATE_MUTATION, {
            "id": op.id,
            "entity": op.entity,
            "lastOverhaulDate": op.last_overhaul_date,
            "tags": op.tags,
        }
