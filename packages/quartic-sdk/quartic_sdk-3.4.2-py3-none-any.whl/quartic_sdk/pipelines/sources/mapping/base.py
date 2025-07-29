import os
import logging
from abc import ABC, abstractmethod
from typing import Tuple

import cloudpickle
import pandas as pd

from quartic_sdk.pipelines.settings import settings
from quartic_sdk.pipelines.helpers.connector_state_mixin import ConnectorStateMixin

logger = logging.getLogger(__name__)


class MappingProcessor(ABC, ConnectorStateMixin):
    """
    Base class for enriching/mapping source connector data
    """

    STATE_BASE_DIR = settings.mapping_connector_state_directory

    @classmethod
    @abstractmethod
    def get_source_classes(cls) -> list[str]:
        raise NotImplemented

    @abstractmethod
    def process(self, df: pd.DataFrame, connector_id: int) -> list[Tuple[str, dict]]:
        raise NotImplemented

