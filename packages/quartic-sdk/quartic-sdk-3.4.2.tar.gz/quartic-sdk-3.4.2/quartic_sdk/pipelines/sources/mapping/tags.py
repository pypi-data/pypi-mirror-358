import logging
import os
from datetime import datetime
from typing import Tuple

import pandas as pd

from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from quartic_sdk.pipelines.sources.mapping.base import MappingProcessor
from quartic_sdk.graphql_client import GraphqlClient

logger = logging.getLogger(__name__)

TAG_DETAILS_QUERY = """
query MyQuery($names: [String!]) {
  __typename
  Tag(name_In: $names) {
    id
    name
    shortName
    asset {
      id
    }
    uom {
      id
      name
      symbol
    }
    valueTable
  }
}
"""
ASSET_DETAILS_QUERY = """
query MyQuery($ids: [String!]) {
  __typename
  Asset(id_In: $ids) {
      id
      name
      tags {
        id
        name
        shortName
      }
      entity {
        id
        name
        entityTemplate {
          id
          name
          entityType {
            name
            id
          }
        }
        attributeValues {
          id
          value
          attribute {
            name
            id
            attributeType
          }
        }
      }
    }
}
"""
AH_ENTITY_QUERY = """
query MyQuery($ids: [String!]) {
  __typename
  AhEntity(id_In: $ids) {
    id
    name
  }
}
"""
PROCESS_UNIT_HIERARCHY = "A_1"
WORK_CELL_HIERARCHY = "A_2"


class TagMappingProcessor(MappingProcessor):
    @classmethod
    def get_source_classes(cls):
        return [
            CONNECTOR_CLASS.Opcua.value,
        ]

    def process(self, df: pd.DataFrame, connector_id: int):
        client = GraphqlClient.get_graphql_client_from_env()
        tag_names = set(
            df["datapoints"].apply(lambda dps: [dp["id"] for dp in dps]).explode()
        )

        # Fetch tag details
        response = client.execute_query(TAG_DETAILS_QUERY, {"names": list(tag_names)})
        tags_by_name = {t["name"]: t for t in response["data"]["Tag"] if t.get("asset")}
        missing_tags = set(filter(lambda t: t not in tags_by_name, tag_names))
        if missing_tags:
            logger.error(f"Ignoring tags {missing_tags} (tag not found)")
        tag_names = tag_names - missing_tags

        # Fetch asset details
        asset_ids = {t["asset"]["id"] for t in tags_by_name.values()}
        response = client.execute_query(ASSET_DETAILS_QUERY, {"ids": list(asset_ids)})
        assets_by_id = {a["id"]: a for a in response["data"]["Asset"]}

        pu_wc_ids = set()
        for asset in assets_by_id.values():
            if not asset["entity"]["attributeValues"]:
                logger.warning(f"Unexpected empty attr values for asset {asset}")
                continue

            # Fetch workcell/production unit
            pu_wc_attr = next(
                filter(
                    lambda a: a["attribute"]["attributeType"]
                    in [PROCESS_UNIT_HIERARCHY, WORK_CELL_HIERARCHY],
                    asset["entity"]["attributeValues"],
                ),
                None,
            )
            if not pu_wc_attr:
                logger.warning(f"No PU/WC set for asset {asset}")
                continue

            pu_wc_id = pu_wc_attr["value"]
            asset["pu_wc_id"] = pu_wc_id
            pu_wc_ids.add(pu_wc_id)

            # Area and enterprice
            for attr in asset["entity"]["attributeValues"]:
                name = attr["attribute"]["name"]
                if name.lower() in ["area", "enterprise", "cell", "unit"]:
                    asset[name.lower()] = attr["value"]

        response = client.execute_query(AH_ENTITY_QUERY, {"ids": list(pu_wc_ids)})
        pu_wc_by_id = {a["id"]: a for a in response["data"]["AhEntity"]}

        # Prepare enriched payloads
        res = []
        for idx, row in df.iterrows():
            for dp in row["datapoints"]:
                tag_name = dp["id"]
                if tag_name not in tags_by_name:
                    logger.warning(f"Ignored data point {dp} (tag not found)")
                    continue

                tag = tags_by_name[tag_name]
                asset_id = tag.get("asset", {}).get("id", None)
                if not asset_id:
                    logger.warning(f"No asset found for tag {tag}")
                    continue

                tag_key = tag["shortName"]
                if not tag_key:
                    logger.info(f"Skipping tag {tag} (no short name)")
                    continue

                value_table = tag["valueTable"] or {}
                tag_value = {
                    "name": tag["name"],
                    "value": value_table.get(str(dp["value"]), dp["value"]),
                    "timestamp": datetime.fromtimestamp(
                        row["timestamp"] / 1000
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "quality": dp["quality"],
                    "uom": (tag["uom"] or {}).get("name", None),
                }
                # Create new asset entry/message
                asset = assets_by_id.get(asset_id, None)
                if not asset:
                    logger.error(f"Could not find asset {asset_id} for tag {tag}")
                    continue
                pu_wc = (
                    pu_wc_by_id.get(asset["pu_wc_id"], None)
                    if "pu_wc_id" in asset
                    else None
                )
                message = {
                    "id": asset["id"],
                    "name": asset["name"],
                    "class": asset["entity"]["entityTemplate"]["name"],
                    "procedure_unit": pu_wc["name"] if pu_wc else None,
                    "area": asset.get("area", None),
                    "unit": asset.get("unit", None),
                    "cell": asset.get("cell", None),
                    "enterprise": asset.get("enterprise", None),
                    tag_key: tag_value,
                    "tags": [tag_key],
                }
                res.append((asset["name"], message))

        # Forward fill tag data
        if os.environ.get("MAPPING_FFILL_ENABLED", "true").lower() == "true":
            logger.info("Forward filling")
            state = self.get_state(connector_id)
            self.update_state(res, state)
            self.ffill_from_state(res, assets_by_id, state)
            self.write_state(state, connector_id)
            for _, m in res:
                # Remove temporary tags key
                m.pop("tags", None)

        return res

    def ffill_from_state(
        self, messages: list[Tuple[str, dict]], assets: dict, state: dict
    ):
        tags = state.get("tags", {})
        if not tags:
            return

        for _, message in messages:
            asset_id = message["id"]
            asset = assets[asset_id]
            for tag in asset["tags"]:
                tag_key = tag["shortName"]
                if not tag_key:
                    continue
                if tag_key in message:
                    continue
                if tag["name"] not in tags:
                    logger.debug(f"Could not ffill tag {tag['name']} (not in state)")
                    continue
                message[tag_key] = {**tags[tag["name"]]}

    def update_state(self, messages: list[Tuple[str, dict]], state: dict):
        tags = state.setdefault("tags", {})
        for _, asset in messages:
            for tag_key in asset["tags"]:
                tag = asset[tag_key]
                tags[tag["name"]] = tag
