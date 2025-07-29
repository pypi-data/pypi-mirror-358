
"""
The given file contains the class to refer to the Context Frame Occurrence entity
"""
import quartic_sdk.utilities.constants as Constants
from quartic_sdk.core.entities.base import Base


class ContextFrameOccurrence(Base):
    """
    The given class refers to the context frame occurrence entity which is created
    based upon the context frame occurrence object returned from the API
    """

    def __repr__(self):
        """
        Override the method to return the asset name with id
        """
        return f"<{Constants.CONTEXT_FRAME_OCCURRENCE_ENTITY}: {self.id}>"
