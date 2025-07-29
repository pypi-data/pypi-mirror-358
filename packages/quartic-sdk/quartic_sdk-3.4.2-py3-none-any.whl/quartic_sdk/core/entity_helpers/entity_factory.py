
from quartic_sdk.core.entities.type_mapping import ENTITY_DICTIONARY
from quartic_sdk.core.entity_helpers.entity_list import EntityList


class EntityFactory:
    """
    The factory is used to create the respective entities depending upon
    the requirements
    """

    def __new__(cls, class_type, body, api_helper):
        """
        The method initializes a copy of the required entity based upon the
        passed parameters
        :param class_type: Type of the class to be created
        :param body: Body through which the entity is to be created
        :param api_helper: APIHelper instance
        """
        if type(body) == list:
            return cls.follow_list_strategy(class_type, body, api_helper)
        return cls.follow_single_strategy(class_type, body, api_helper)

    @classmethod
    def follow_single_strategy(cls, class_type, body, api_helper):
        """
        The given method creates a new instance of the object as required
        based upon the class_type
        :param class_type: Type of the class to be created
        :param body: Body through which the entity is to be created
        :param api_helper: APIHelper instance
        """
        return ENTITY_DICTIONARY[class_type](body, api_helper)

    @classmethod
    def follow_list_strategy(cls, class_type, body, api_helper):
        """
        The given method creates a new instance of BaseEntityList with
        the objects as required based upon the class_type
        :param class_type: Type of the class to be created
        :param body: Body through which the entity is to be created
        :param api_helper: APIHelper instance
        """
        entities_list = EntityList(class_type=class_type)
        for each_element in body:
            entities_list.add(ENTITY_DICTIONARY[class_type](each_element, api_helper))
        return entities_list
