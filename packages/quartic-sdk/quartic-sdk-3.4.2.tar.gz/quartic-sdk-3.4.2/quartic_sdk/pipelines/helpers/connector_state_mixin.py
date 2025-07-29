import os
import logging
from contextlib import contextmanager

import cloudpickle

logger = logging.getLogger(__name__)


class ConnectorStateMixin:
    """Common methods for fetching and writing connector state"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __get_state_pickle_file(self, connector_id: int):
        if not os.path.exists(self.STATE_BASE_DIR):
            logger.info(f"Creating state dir {self.STATE_BASE_DIR}")
            os.system(f"mkdir -p {self.STATE_BASE_DIR}")

        return f"{self.STATE_BASE_DIR}/state_tags_{connector_id}.pkl"

    def get_state(self, connector_id: int):
        filename = self.__get_state_pickle_file(connector_id)
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return cloudpickle.load(f) or {}
        return {}

    def write_state(self, state: dict, connector_id: int):
        filename = self.__get_state_pickle_file(connector_id)
        with open(filename, "wb") as f:
            cloudpickle.dump(state, f)

    @contextmanager
    def open_state(self, connector_id: int):
        state = self.get_state(connector_id)
        yield state
        self.write_state(state, connector_id)
