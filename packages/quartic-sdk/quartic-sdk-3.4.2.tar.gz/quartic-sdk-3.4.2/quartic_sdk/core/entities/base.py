"""
The given file contains the class to refer to the base class for entity creation
"""
import quartic_sdk.utilities.constants as Constants


class Base:
    """
    The base class which is used for creating all the required instances
    of specific types
    """

    def __init__(self, body_json, api_helper):
        """
        Initialize the given entity. As a part of the initialization, we set the keys
        of `body_json` as the attributes of the class
        :param body_json: Dict containing the body of the entity
        :param api_helper: APIHelper class instance containing configuration details
        """
        for key in body_json:
            setattr(self, key, body_json[key])
        self.api_helper = api_helper

    def get(self, name):
        """
        Return the value of the given `name` attribute
        :param name: (string) The attribute name to be returned
        :return: The returned attribute value
        """
        return getattr(self, name)

    def __str__(self):
        """
        Return the stringifed version of the representation
        """
        return self.__repr__()

    def __eq__(self, other):
        """
        Override equals to check equality of all attributes
        :param other: The other object, to which we are comparing
        :return: (bool) Whether they are equal
        """
        assert isinstance(self, type(other))
        return len(
            self.__dict__) == len(
            other.__dict__) and all(
            self.__dict__[key] == other.__dict__[key] for key in self.__dict__)
