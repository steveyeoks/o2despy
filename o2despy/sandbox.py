import datetime as dt
import os
import random
import threading
import time
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from commons.file_config import FileConfig
from sortedcontainers import SortedSet
from o2despy.action import Action
from o2despy.event import Event
from o2despy.hour_counter import HourCounter


class ISandbox(ABC):
    """ This abstract class aims to define the abstract properties and
    abstract methods for Sandbox.

    Sandbox is a basic class for the object-oriented discrete event
    simulation (O2DES) framework.

    In its extension,
    the future events can be scheduled to happen at the scheduled time,
    and then invoked to happen by the scheduled time.
    """

    @property
    @abstractmethod
    def index(self):
        """ Unique index in sequence for all class instances. """
        pass

    @property
    @abstractmethod
    def code(self):
        """ Identifier for the class instance. """
        pass

    @property
    @abstractmethod
    def seed(self):
        """ Random seed. """
        pass

    @property
    @abstractmethod
    def parent(self):
        """ Parent object if any, otherwise None.

        The class of parent object inherits from Sandbox.
        """
        pass

    @property
    @abstractmethod
    def children(self):
        """ All the children.

        All the classes of children inherit from Sandbox.
        """
        pass

    # @property
    # @abstractmethod
    # def log_file(self):
    #     """ File name of log file.  """
    #     pass

    @property
    @abstractmethod
    def debug_mode(self):
        """ Whether under debug mode. """
        pass

    @property
    @abstractmethod
    def clock_time(self):
        """ Current simulation time. """
        pass

    @property
    @abstractmethod
    def head_event_time(self):
        """ Scheduled time of the earliest future event. """
        pass

    @abstractmethod
    def warmup(self, **kwargs):
        """ Warm up until a given condition is satisfied. """
        pass

    @abstractmethod
    def run(self, **kwargs):
        """ Run until a given condition is satisfied. """
        pass


class Sandbox(ISandbox):
    """ A basic class for the object-oriented discrete event simulation
    (O2DES) framework.

    This class defines the properties and methods for Sandbox.

    The future events can be scheduled to happen at the scheduled time,
    and then invoked to happen by the scheduled time.
    """
    _count = 0

    def __init__(self, seed=0, code=None):
        """ Initialization.

        Args:
            seed: random seed.
            code: identifier for sandbox.
        """
        Sandbox._count += 1
        self._index = Sandbox._count
        self._code = code
        self._seed = None
        self._parent = None
        self._children = []
        self._hour_counters = []
        self._on_warmup = Action().add(self._warmup_handler)
        self._clock_time = dt.datetime.min
        self._future_event_list = SortedSet()
        self._event_count = 0
        self._real_time_for_last_run = None
        # self._log_file = None
        self._debug_mode = False
        self._thread_event = None
        self.seed = seed
        self._main_hc = self.add_hour_counter()
        self.is_first_event_scheduled = False
        self.first_event_clock_time = dt.datetime.min

    def __str__(self):
        """ A string representing the class instance. """
        return f"{self.__class__.__name__}#{self._code or self._index}"

    @property
    def index(self):
        """ Unique index in sequence for all class instances. """
        return self._index

    @property
    def code(self):
        """ Identifier for the class instance. """
        return self._code or f"{self.__class__.__name__}#{self._index}"

    @property
    def seed(self):
        """ Random seed. """
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value
        random.seed(value)
        np.random.seed(value)

    @property
    def parent(self):
        """ Parent object if any, otherwise None.

        The class of parent object inherits from Sandbox.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def children(self):
        """ All the children.

        All the classes of children inherit from Sandbox.
        """
        return tuple(self._children)

    @property
    def main_hc(self):
        """ Main Hour Counter """
        return self._main_hc

    @property
    def hour_counters(self):
        """ All the hour counters added to current instance. """
        return tuple(self._hour_counters)

    @property
    def on_warmup(self):
        """ All the actions to trigger immediately after warm-up. """
        return self._on_warmup

    @property
    def future_event_list(self):
        """ Events to be invoked in the future. """
        return self._future_event_list

    @property
    def event_count(self):
        """ Count value of events which is owned by current instance and
        has been invoked.
        """
        return self._event_count

    # @property
    # def log_file(self):
    #     """ File name of log file.  """
    #     return self._log_file
    #
    # @log_file.setter
    # def log_file(self, log_file):
    #     self._log_file = log_file
    #     if self._log_file:
    #         return
    #     with os.fdopen(
    #             os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
    #             mode='w', encoding=FileConfig.ENCODING_MODE) as f:
    #         pass

    @property
    def debug_mode(self):
        """ Whether under debug mode. """
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value

    @property
    def clock_time(self):
        """ Current simulation time. """
        if self._parent is None:
            return self._clock_time
        return self._parent.clock_time

    @property
    def head_event(self):
        """ Earliest event which has not been invoked. """
        head_event_ = None
        if self._future_event_list:
            head_event_ = self._future_event_list[0]
        for child in self._children:
            child_head_event = child.head_event
            if head_event_ is None or \
                    child_head_event and child_head_event < head_event_:
                head_event_ = child_head_event
        return head_event_

    @property
    def head_event_time(self):
        """ Scheduled time of the earliest future event. """
        return self.head_event.scheduled_time if self.head_event else None

    def observe_event(self):
        """ Observe the total event count that is owned by current class
        instance and had been invoked.
        """
        self._event_count += 1

    def add_child(self, child):
        """ Add a child object (inherit from Sandbox).

        Args:
            child: child object that inherits from Sandbox.

        Returns:
            child: child object which is added.
        """
        self._children.append(child)
        child.parent = self
        self._on_warmup.add(child.on_warmup)
        return child

    def add_hour_counter(self, keep_history=False):
        """ Create a hour counter and add it into model.

        Args:
            keep_history: whether keep history of each observation.

        Returns:
            hc: target hour counter.
        """
        hc = HourCounter(self)
        self._hour_counters.append(hc)
        self._on_warmup.add(hc.warmup)
        return hc

    def warmup(self, **kwargs):
        """ Warm up until a given condition is satisfied.

        Args:
            kwargs: a keyword argument, which can be:
                * till: warm up until the specified clock-time.
                * period: warm up for the specified time delay.

        Returns:
            whether simulation can be continued.

        Raises:
            ValueError: an error occurred when passing an invalid argument.
        """
        if 'till' in kwargs:
            return self.warmup_until(kwargs['till'])
        elif 'period' in kwargs:
            return self.warmup_for_period(kwargs['period'])
        else:
            raise ValueError("missing a valid keyword arguments")

    def warmup_until(self, till):
        """ Warm up until the specified clock time.

        Args:
            till: the specified clock time.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.warmup_until(till)
        result = self.run(terminate=till)
        self._on_warmup.invoke()
        return result

    def warmup_for_period(self, period):
        """ Warm up for the specified time delay.

        Args:
            period: the specified time delay.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.warmup_for_period(period)
        return self.warmup_until(till=self.clock_time + period)

    def update_first_event_clock_time(self, clock_time=None):
        """ Update the first event clock time. """
        # update the parent for first event
        if not self.is_first_event_scheduled:
            self.is_first_event_scheduled = True
        # scroll to the top parent
        if self._parent is not None:
            return self._parent.update_first_event_clock_time(clock_time)
        # update the first event clock time
        self.first_event_clock_time = clock_time

    def schedule(self, action, clock_time=None, tag=None, *args, **kwargs):
        """ Schedule an event to be invoked at the specified clock-time or
        after the specified time delay or at the current clock time.

        Args:
            action: a callable object.
            clock_time: scheduled time to invoke the event.
            tag: tag of the event.
            args: partial applied positional arguments for action.
            kwargs: partial applied keyword arguments for action.

        Raises:
            TypeError: An error occurred when passing in an invalid action
                or clock_time.
        """
        # capture the clocktime for the first event
        if not self.is_first_event_scheduled:
            self.is_first_event_scheduled = True
            self.update_first_event_clock_time(self.clock_time)

        if not callable(action):
            raise TypeError("Unexpected type of action, expect a callable object.")
        if clock_time is None:
            clock_time = self.clock_time + dt.timedelta(seconds=0)
        elif isinstance(clock_time, dt.timedelta):
            clock_time = self.clock_time + clock_time
        elif isinstance(clock_time, dt.datetime):
            pass
        elif isinstance(clock_time, pd.Timestamp):
            clock_time = clock_time.to_pydatetime()
        else:
            raise TypeError(f"Unexpected type of clock_time: {clock_time}.")
        future_event = Event(
            action=Action.partial(action, *args, **kwargs),
            scheduled_time=clock_time, owner=self, tag=tag)
        self._future_event_list.add(future_event)
        func = future_event.action.subactions[0]
        if hasattr(func, 'func'):
            func = func.func


    def run(self, **kwargs):
        """ Run until a given condition is satisfied.

        Args:
            kwargs: a keyword argument, which can be:
                * duration: run for the specified duration.
                * terminate: run until the specified clock time.
                * event_count: run for the specified number of events.
                * speed: run for a duration of a specified multiple of
                    the CPU time span (since last run).

        Returns:
            whether simulation can be continued.

        Raises:
            ValueError: An error occurred when passing an invalid argument.
        """
        if kwargs == {}:
            return self.run_once()
        elif 'terminate' in kwargs:
            return self.run_until(kwargs['terminate'])
        elif 'duration' in kwargs:
            return self.run_for_period(kwargs['duration'])
        elif 'event_count' in kwargs:
            return self.run_multiple_times(kwargs['event_count'])
        elif 'speed' in kwargs:
            return self.run_at_speed(kwargs['speed'])
        else:
            raise ValueError("invalid argument")

    def run_once(self):
        """ Pop one event from future event list and invoke the event.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.run_once()
        head = self.head_event
        if head is None:
            return False
        head.owner.future_event_list.discard(head)
        self._clock_time = head.scheduled_time
        head.invoke()
        return True

    def run_until(self, terminate):
        """ Run until the specified clock time.

        Args:
            terminate: a clock time to terminate.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.run_until(terminate)
        n = 0
        step_time = time.time()
        while True:
            head = self.head_event
            if head is None or head.scheduled_time > terminate:
                self._clock_time = terminate
                return head is not None
            self.run_once()
            n += 1
            if n % 1000 == 0:
                current_time = time.time()
                step_time = current_time

    def run_for_period(self, duration):
        """ Run for the specified period.

        Args:
            duration: a period to run.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.run_for_period(duration)
        return self.run_until(terminate=self.clock_time + duration)

    def run_multiple_times(self, event_count):
        """ Run for the specified number of events.

        Args:
            event_count: number of events to run.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.run_multiple_times(event_count)
        while event_count > 0:
            if not self.run_once():
                return False
            event_count -= 1
        return True

    def run_at_speed(self, speed):
        """ Run for a duration of a specified multiple of the CPU period
        (since last run).

        Args:
            speed: a multiple value.

        Returns:
            whether simulation can be continued.
        """
        if self._parent is not None:
            return self._parent.run_at_speed(speed)
        rtn = True
        if self._real_time_for_last_run is not None:
            duration = dt.datetime.now() - self._real_time_for_last_run
            duration = duration.total_seconds() * speed
            rtn = self.run(terminate=self.clock_time + duration)
        self._real_time_for_last_run = dt.datetime.now()
        return rtn

    def pause(self):
        """ Pause the model.

        Returns:
            whether pause successfully.
        """
        if self._parent is not None:
            return self._parent.pause()
        if self._thread_event is None:
            self._thread_event = threading.Event()
            self._thread_event.wait()
            return True
        return False

    def resume(self):
        """ Resume the model.

        Returns:
            whether resume successfully.
        """
        if self._parent is not None:
            return self._parent.resume()
        if self._thread_event is not None:
            self._thread_event.set()
            self._thread_event = None
            return True
        return False

    def _warmup_handler(self):
        """ The default event to invoke at the end of warmup. """
        pass

    # def _log(self, args):
    #     """ Log to file.
    #
    #     Args:
    #         args: iterable object with information to log.
    #     """
    #     if self._log_file is None:
    #         return
    #     time_str = self.clock_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    #     str_ = "".join(f"{arg}\t" for arg in args)
    #     str_ = f"{time_str}\t{self._code}\t{str_}\n"
    #     with os.fdopen(
    #             os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
    #             mode='a', encoding=FileConfig.ENCODING_MODE) as f:
    #         f.write(str_)
