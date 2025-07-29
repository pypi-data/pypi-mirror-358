import logging
from typing import Tuple

from quartic_sdk.pipelines.sinks.internal.operations.handlers.base import (
    GQLOperationHandler,
)
from quartic_sdk.pipelines.sinks.internal.operations.operations import (
    TagCreate,
    TagUpdate,
    TagDelete,
)

logger = logging.getLogger(__name__)

TAG_CREATE_MUTATION = """
mutation createTag(
    $edgeConnector: ID!,
    $name: String!,
    $tagType: TagTagTypeEnumCreate!
) {
    TagCreate(newTag: {
        edgeConnector: $edgeConnector,
        name: $name,
        tagType: $tagType
    }) {
        ok
        errors {
            field
            messages
        }
    }
}
"""
TAG_UPDATE_MUTATION = """
mutation updateTag(
    $id: ID!,
    $edgeConnector: ID!,
    $name: String!,
    $tagType: TagTagTypeEnumUpdate!
) {
    TagUpdate(updateTag: {
        id: $id,
        edgeConnector: $edgeConnector,
        name: $name,
        tagType: $tagType
    }) {
        ok
        errors {
            field
            messages
        }
    }
}
"""
TAG_DELETE_MUTATION = """
mutation deleteTag($id: ID!) {
    TagDelete(id: $id) {
        ok
        errors {
            field
            messages
        }
    }
}
"""


class TagCreateHandler(GQLOperationHandler[TagCreate]):
    @classmethod
    def get_optype(cls):
        return TagCreate

    def get_success_field(self):
        return "data.TagCreate.ok"

    def get_query(self, op: TagCreate):
        return TAG_CREATE_MUTATION, {
            "edgeConnector": op.edge_connector,
            "name": op.name,
            "tagType": op.tag_type,
        }


class TagUpdateHandler(GQLOperationHandler[TagUpdate]):
    @classmethod
    def get_optype(cls):
        return TagUpdate

    def get_success_field(self):
        return "data.TagUpdate.ok"

    def get_query(self, op: TagUpdate):
        return TAG_UPDATE_MUTATION, {
            "id": op.id,
            "edgeConnector": op.edge_connector,
            "name": op.name,
            "tagType": op.tag_type,
        }


class TagDeleteHandler(GQLOperationHandler[TagDelete]):
    @classmethod
    def get_optype(cls):
        return TagDelete

    def get_success_field(self):
        return "data.TagDelete.ok"

    def get_query(self, op: TagDelete) -> Tuple[str, dict]:
        return TAG_DELETE_MUTATION, {"id": op.id}
