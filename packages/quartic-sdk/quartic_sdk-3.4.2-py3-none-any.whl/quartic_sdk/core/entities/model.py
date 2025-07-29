import base64

import cloudpickle

import quartic_sdk.utilities.constants as Constants
from quartic_sdk.core.entities.base import Base
from quartic_sdk.model.helpers import ModelUtils


class Model(Base):
    """
    The given class refers to the Model entity which is created based upon the
    Model object returned from the API
    """

    def __init__(self, body_json, api_helper):
        super().__init__(body_json, api_helper)
        self.id = self.model_id

    def __repr__(self):
        """
        Override the method to return the Model with model name
        """
        return f"<{Constants.MODEL_ENTITY}: {self.model_name}>"

    def model_instance(self, query_params={}):
        """
        Returns the model object saved in the model
        :param query_params: Dictionary of filter conditions
        :return:    Returns a Model which is subclass of BaseQuarticModel
        """
        response = self.api_helper.call_api(Constants.CMD_MODEL_ENDPOINT, method_type=Constants.API_GET,
                                            path_params=[self.model_id],
                                            query_params=query_params,
                                            body={})
        response.raise_for_status()
        model_string = response.json()['model']
        checksum_received = model_string[:32]
        decoded_model = base64.b64decode(model_string[32:])
        assert ModelUtils.get_checksum(model_string[32:].encode()) == checksum_received
        return cloudpickle.loads(decoded_model)
