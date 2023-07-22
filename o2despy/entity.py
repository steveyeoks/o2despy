from abc import ABC


class IEntity(ABC):
    """ An abstract class for entity.

    This abstract class defines the abstract properties for an entity.
    """

    @property
    def index(self):
        """ Unique index in sequence for all class instances. """
        pass

    @property
    def id(self):
        """ Identifier for the class instance. """
        pass


class Entity(IEntity):
    """ This class aims to represent an entity.

    This class defines the properties for an entity.
    """
    _count = 0

    def __init__(self, id=None):
        """ Initialization.

        Args:
            code: identifier of the entity.
        """
        Entity._count += 1
        self._index = Entity._count
        self._id = id

    def __str__(self):
        """ A string representing the class instance. """
        return f"<{self.__class__.__name__}#{self._id or self._index}>"

    @property
    def index(self):
        """ Unique index in sequence for all class instances. """
        return self._index

    @property
    def id(self):
        """ Identifier for the class instance. """
        return self._id or f"{self.__class__.__name__}#{self._index}"
