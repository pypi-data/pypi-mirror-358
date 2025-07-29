from quartic_sdk.core.entities.base import Base
import quartic_sdk.utilities.constants as Constants


class EventFrameOccurrence(Base):
    """
    The given class refers to the event frame occurrence entity which is created based upon the
    event frame occurrence object returned from the API
    """

    def __init__(self, body_json, api_helper):
        super().__init__(body_json, api_helper)
        self.__dict__['event_frame_name'] = self.__dict__.pop('name')

    def __repr__(self):
        """
        Override the method to return the event frame occurrence name
        """
        return f"<{Constants.EVENT_FRAME_OCCURRENCE_ENTITY}: {self.id}>"
