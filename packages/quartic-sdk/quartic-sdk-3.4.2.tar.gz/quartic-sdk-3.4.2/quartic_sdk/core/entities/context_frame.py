
"""
The given file contains the class to refer to the Context Frame entity
"""
from quartic_sdk.core.entities.base import Base
import quartic_sdk.utilities.constants as Constants


class ContextFrame(Base):
    """
    The given class refers to the context frame entity which is created based
    upon the context frame object returned from the API
    """

    def __repr__(self):
        """
        Override the method to return the asset name with id
        """
        return f"<{Constants.CONTEXT_FRAME_ENTITY}: {self.id}>"

    def occurrences(self, query_params={}):
        """
        Return the list of occurrences for the given context frame
        :param query_params: Dictionary of filter conditions
        """
        from quartic_sdk.core.entity_helpers.entity_factory import EntityFactory
        occurrences_response = self.api_helper.call_api(
            Constants.GET_CONTEXT_FRAME_OCCURRENCES, Constants.API_GET, [self.id], query_params).json()
        return EntityFactory(
            Constants.CONTEXT_FRAME_OCCURRENCE_ENTITY,
            occurrences_response,
            self.api_helper)
