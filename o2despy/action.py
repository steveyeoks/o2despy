from collections.abc import Iterable
from functools import partial
from inspect import signature


class Action(object):
    """ This class aims to encapsulate a group of subactions.

    These subactions are the methods which have features as below:
    * have same number and type of unassigned arguments;
    * have no return value.

    For the subaction with assigned arguments, we call functools.partial to
    partially apply positional arguments and keyword arguments to the method.

    Attributes:
        subactions: all the encapsulated callable subactions.
        partial: an handy interface for construction of a subaction.
        check_option: whether to check when adding subactions.
    """
    partial = partial
    check_option = True

    def __init__(self, *args, **kwargs):
        """ Initialization.

        Args:
            args: a variable number of unassigned positional argument types.
            kwargs: a variable number of unassigned keyword argument types.
        """
        self._argcount = len(args) + len(kwargs)
        self._args = args
        self._kwargs = kwargs
        self._subactions = []

    def __len__(self):
        """ Total number of Encapsulated methods. """
        return len(self._subactions)

    def __add__(self, value):
        """ Combine all the subactions of self and value.

        Args:
            value: an Action or a callable object.

        Returns:
            new_action: a new Action with all subactions of self and value.
        """
        new_action = Action(*self._args, **self._kwargs)
        new_action.add(self, False)
        new_action.add(value)
        return new_action

    @property
    def subactions(self):
        """ All the encapsulated callable objects. """
        return tuple(self._subactions)

    def invoke(self, *args, **kwargs):
        """ Invoke all the encapsulated subactions.

        Args:
            args: a variable number of positional arguments.
            kwargs: a variable number of keyword arguments.
        """
        for func in self._subactions:
            func(*args, **kwargs)

    def clear(self):
        """ Clear the encapsulated actions. """
        self._subactions.clear()

    def add(self, action, check=check_option):
        """ Encapsulate a subaction.

        Args:
            action: the subaction(s) to be encapsulated, which could be
                an Action, a method, or an iterable object of methods.
            check: whether to check the subaction(s).

        Returns:
            self: the current Action object itself.
        """
        if isinstance(action, Action):
            subactions = action.subactions
        elif isinstance(action, dict):
            subactions = action.values()
        elif isinstance(action, Iterable):
            subactions = action
        else:
            subactions = (action,)
        for subaction in subactions:
            self._add_subaction(subaction, check)
        return self

    def _add_subaction(self, subaction, check):
        """ Internal method for encapsulating a subaction.

        Args:
            subaction: the subaction to encapsulate.
            check: whether to check the subaction.
        """
        if check:
            self._check_subaction(subaction)
        self._subactions.append(subaction)

    def _check_subaction(self, subaction):
        """ Check whether a subaction is valid.

        Args:
            subaction: the subaction to check.

        Raises:
            TypeError: an error occurred when passing in an invalid method.
        """
        if not callable(subaction):
            raise TypeError(f"non-callable type: {subaction}.")
        method = subaction
        argcount = 0
        if isinstance(subaction, partial):
            method = subaction.func
            argcount -= len(subaction.args) + len(subaction.keywords)
        if not hasattr(method, '__name__'):
            raise TypeError(f"Unexpected type of subaction: {method}.")
        method_signature = signature(method)
        for _, param in method_signature.parameters.items():
            if param.default is param.empty:
                argcount += 1
        if argcount != self._argcount:
            raise TypeError(
                f"expect arguments number of {self._argcount}, "
                f"but {method.__qualname__} takes {argcount}.")
