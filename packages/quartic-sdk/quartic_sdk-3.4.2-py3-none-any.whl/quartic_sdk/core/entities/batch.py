
"""
The given file contains the class to refer to the Batch entity
"""
from quartic_sdk.core.entities.base import Base
import quartic_sdk.utilities.constants as Constants


class Batch(Base):
    """
    The given class refers to the batch entity which is created based upon the batch
    object returned from the API
    """

    def __repr__(self):
        """
        Override the method to return the asset name
        """
        return f"<{Constants.BATCH_ENTITY}: {self.batch_name}>"
