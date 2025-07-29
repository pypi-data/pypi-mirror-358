

class EntityListIterator:
    """
    The given class is the entity list iterator which will be used to iterate
    for the given list of entities
    """

    def __init__(self, base_entity_list):
        """
        Initialize the iterator. We set the current index as 0
        :param base_entity_list: Refers to the EntityList object
        """
        self._base_entity_list = base_entity_list
        self._index = 0

    def __next__(self):
        """
        Return the subsequent iteration results starting from 0 as index
        """
        if self._base_entity_list.count() > self._index:
            self._index +=1
            return self._base_entity_list[self._index-1]
        raise StopIteration
