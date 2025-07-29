from quartic_sdk.core.entities.base import Base
import quartic_sdk.utilities.constants as Constants


class EventFrame(Base):
    """
    The given class refers to the event frame entity which is created based upon the
    event frame object returned from the API
    """

    def __repr__(self):
        """
        Override the method to return the event frame name
        """
        return f"<{Constants.EVENT_FRAME_ENTITY}: {self.name}>"

    def occurrences(self, start_time, stop_time, query_params={}):
        """
        The given method returns the list of event frame occurrences for the given asset in the given time frame
        :param start_time: (epoch) Start_time of event frame occurrence
        :param stop_time: (epoch) Stop_time of event frame occurrence
        :param query_params: Dictionary of filter conditions
        """
        if not (isinstance(start_time, int) and isinstance(stop_time, int)):
            raise TypeError("start_time and end_time epoch should be int")

        from quartic_sdk.core.entity_helpers.entity_factory import EntityFactory
        event_frame_occurrence_response = self.api_helper.call_api(
            Constants.GET_EVENT_FRAME_OCCURRENCES,
            Constants.API_GET,
            path_params=[self.id, start_time, stop_time],
            query_params=query_params).json()
        return EntityFactory(
            Constants.EVENT_FRAME_OCCURRENCE_ENTITY,
            event_frame_occurrence_response,
            self.api_helper)
