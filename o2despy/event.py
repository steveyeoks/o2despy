from functools import total_ordering
from o2despy.action import Action


@total_ordering
class Event(object):
    """ This class aims to describe an event.

    Attributes:
        action: the object to be called when the event is invoked.
        scheduled_time: the time to invoke the event.
        owner: the object that schedules the event.
        tag: tag of the event.
    """
    _count = 0

    def __init__(self, action, scheduled_time, owner, tag=None):
        """ Initialization.

        Args:
            action: the object to be called when the event is invoked.
            scheduled_time: the time to invoke the event.
            owner: the object that schedules the event.
            tag: tag of the event.
        """
        Event._count += 1
        self._index = Event._count
        self._tag = tag
        self._owner = owner
        self._action = Action().add(action)
        self._scheduled_time = scheduled_time

    def __str__(self):
        """ A string representing the class instance. """
        str_ = f"{self._tag or self.__class__.__name__}#{self._index}"
        return str_

    def __hash__(self):
        """ Make the class object hashable.

        Returns:
            Hash value for the index of object.
        """
        return hash(self._index)

    def __eq__(self, other):
        """ Compare self and other by scheduled time and index.

        Args:
            other: another event.

        Returns:
            is_equal: whether self and other is equal.
        """
        is_equal = isinstance(other, Event) and \
            self._scheduled_time == other.scheduled_time and \
                self._index == other.index
        return is_equal

    def __lt__(self, other):
        """ Compare self and other by scheduled time and index.

        Args:
            other: another event.

        Returns:
            whether self is less than other.

        Raises:
            TypeError: An error occurred passing in an invalid type.
        """
        if not isinstance(other, Event):
            raise TypeError(f"expect type of Event but got {type(other)}.")
        if self._scheduled_time == other.scheduled_time:
            return self._index < other.index
        else:
            return self._scheduled_time < other.scheduled_time

    @property
    def index(self):
        """ Unique index in sequence for all class instances. """
        return self._index

    @property
    def tag(self):
        """ Tag of the event. """
        return self._tag

    @property
    def owner(self):
        """ The object that schedules the event. """
        return self._owner

    @property
    def scheduled_time(self):
        """ The time to invoke the event. """
        return self._scheduled_time

    @property
    def action(self):
        """ The object to be called when the event is invoked. """
        return self._action

    def invoke(self):
        """ Invoke the event by calling the corresponding method. """
        self._action.invoke()
