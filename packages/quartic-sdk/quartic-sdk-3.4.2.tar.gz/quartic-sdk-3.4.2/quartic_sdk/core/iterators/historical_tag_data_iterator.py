
import json
import pandas as pd
import quartic_sdk.utilities.constants as Constants


class HistoricalTagDataIterator:
    """
    Thee given class is the iterator class for OPCUA data connector
    """

    def __init__(self,
        tags,
        edge_connector_id,
        start_time,
        stop_time,
        api_helper,
        batch_size=Constants.DEFAULT_BATCH_SIZE,
        max_records=None,
        return_type=Constants.RETURN_JSON):
        """
        We initialize the opcua iterator with the given parameters
        :param tags: (BaseEntityList) Refers to the instance of BaseEntityList with
                each containing tags as the individual items
        :param edge_connector_id: ID of Edge connector entity
        :param start_time: (epoch) Start time of the query
        :param stop_time: (epoch) Stop time of the query
        :param batch_size: Expected size of each batch
        :param api_helper: (APIHelper) APIHelper class object
        :param return_type: The param decides whether the data after querying will be
            json(when value is "json") or pandas dataframe(when value is "pd"). By default,
            it takes the value as "json"
        """
        self.tags = tags
        self.edge_connector_id = edge_connector_id
        self.start_time = start_time
        self.stop_time = stop_time
        self.batch_size = batch_size
        self.max_records = max_records
        self.api_helper = api_helper
        self.return_type = return_type

        self._cursor = None
        self._data_call_state = 0

    def create_post_data(self):
        """
        The method creates the post data for the tag data call
        """
        return {
            "tags": [tag.name for tag in self.tags.all()],
            "start_time": self.start_time,
            "end_time": self.stop_time,
            "batch_size": self.batch_size,
            "max_records": self.max_records
        }

    def __iter__(self):
        """
        Return the opcua data iterator with the data fetch state set at 0
        """
        self._data_call_state = 0
        return self

    def __rearrange_json_to_create_data_frame(self, data_frame_json):
        """
        The method rearranges the output of the API json data into dataframe json to return
        dataframee eventually
        """
        reoriented_json = {item["timestamp"]: item["data"] for item in data_frame_json["data_points"]}
        reoriented_json_str = json.dumps(reoriented_json)
        return pd.read_json(reoriented_json_str, orient="index", convert_dates=False,
            convert_axes=False)

    def __next__(self):
        """
        Get the next object in the iteration.
        Note that the return object is inclusive of time ranges
        """
        if self._data_call_state != 0 and self._cursor == "":
            self._data_call_state = 0
            raise StopIteration
        body_json = self.create_post_data()
        tag_data_return = self.api_helper.call_api(
            Constants.POST_OPCUA_DATA, Constants.API_POST, body=body_json,
            path_params=[self.edge_connector_id], query_params={"cursor": self._cursor}).json()
        self._data_call_state = 1

        self._cursor = tag_data_return["cursor"]

        if self.return_type == Constants.RETURN_JSON:
            return tag_data_return["data_points"]

        return self.__rearrange_json_to_create_data_frame(tag_data_return)
