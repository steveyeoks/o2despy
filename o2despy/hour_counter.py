import datetime as dt
import os
from abc import ABC, abstractmethod
from commons.time_tools import timedelta2hours
from commons.file_config import FileConfig


class IReadOnlyHourCounter(ABC):
    """ This abstract class aims to define the abstract properties regarding
    the change of a variable during the simulation.

    In its extension,
    the related read-only statistics is accessible by properties.
    """

    @property
    @abstractmethod
    def last_time(self):
        """ Clock time on last observation. """
        pass

    @property
    @abstractmethod
    def last_count(self):
        """ Count value on last observation. """
        pass

    @property
    @abstractmethod
    def cum_value(self):
        """ Cumulative count value (integral) on time in unit of hours. """
        pass

    @property
    @abstractmethod
    def total_hours(self):
        """ Total working hours since the initial time. """
        pass

    @property
    @abstractmethod
    def total_increment(self):
        """ Total number of increment observed. """
        pass

    @property
    @abstractmethod
    def total_decrement(self):
        """ Total number of decrement observed. """
        pass

    @property
    @abstractmethod
    def increment_rate(self):
        """ Average number of increment (hourly) on observation period. """
        pass

    @property
    @abstractmethod
    def decrement_rate(self):
        """ Average number of decrement (hourly) on observation period. """
        pass

    @property
    @abstractmethod
    def average_count(self):
        """ Average count (hourly) on observation period. """
        pass

    @property
    @abstractmethod
    def average_duration(self):
        """ Average timespan (hour) that a load stays in the activity.

        If it is a stationary process,
        i.e., decrement rate == increment rate.
        It is 0 at the initial status,
        i.e., decrement rate is 0 (no decrement observed).
        """
        pass

    @property
    @abstractmethod
    def working_time_ratio(self):
        """ Ratio value of total working time on observation period. """
        pass

    @property
    @abstractmethod
    def paused(self):
        """ Whether the state is being working. """
        pass

    # @property
    # @abstractmethod
    # def log_file(self):
    #     """ File name of log file. """
    #     pass


class IHourCounter(IReadOnlyHourCounter):
    """ This abstract class aims to define the abstract properties and methods
    regarding the change of a variable during the simulation.

    In its extension,
    the change of the variable can be recorded by methods, and
    the related read-only statistics is accessible by properties.
    """

    @abstractmethod
    def observe_count(self, count, clock_time):
        """ Observe the count value.

        Args:
            count: the observed count value.
            clock_time: the clock time when observation.
        """
        pass

    @abstractmethod
    def observe_change(self, change, clock_time):
        """ Observe the change of the count value.

        Args:
            change: the change of the count value since last observation.
            clock_time: the clock time when observation.
        """
        pass

    @abstractmethod
    def pause(self, clock_time):
        """ Set the state as paused.

        Args:
            clock_time: the clock time when setting.
        """
        pass

    @abstractmethod
    def resume(self, clock_time):
        """ Restart from the state of paused.

        Args:
            clock_time: the clock time when restart.
        """
        pass


class ReadOnlyHourCounter(IReadOnlyHourCounter):
    """ The class aims to define the properties regarding the change of
    a variable during the simulation.

    The related read-only statistics is accessible by properties.
    """

    def __init__(self, hour_counter):
        """ Initialization.

        Args:
            hour_counter: target hour counter.
        """
        self._hour_counter = hour_counter

    @property
    def last_time(self):
        return self._hour_counter.last_time

    @property
    def last_count(self):
        return self._hour_counter.last_count

    @property
    def cum_value(self):
        return self._hour_counter.cum_value

    @property
    def total_hours(self):
        return self._hour_counter.total_hours

    @property
    def total_increment(self):
        return self._hour_counter.total_increment

    @property
    def total_decrement(self):
        return self._hour_counter.total_decrement

    @property
    def increment_rate(self):
        return self._hour_counter.increment_rate

    @property
    def decrement_rate(self):
        return self._hour_counter.decrement_rate

    @property
    def average_count(self):
        return self._hour_counter.average_count

    @property
    def average_duration(self):
        return self._hour_counter.average_duration

    @property
    def working_time_ratio(self):
        return self._hour_counter.working_time_ratio

    @property
    def paused(self):
        return self._hour_counter.paused

    # @property
    # def log_file(self):
    #     return self._hour_counter.log_file


class HourCounter(IHourCounter):
    """ The class aims to define the properties and methods regarding
    the change of a variable during the simulation.

    The change of the variable can be recorded by methods, and
    the related read-only statistics is accessible by properties.
    """

    def __init__(self, sandbox, initial_time=None, keep_history=False):
        """ Initialization.

        Args:
            sandbox: owner of the hour counter.
            initial_time: initial datetime of the hour counter.
            keep_history: whether keep history of each observation.
        """
        self._sandbox = sandbox
        self._initial_time = initial_time or dt.datetime.min
        self._last_time = self._initial_time
        self._last_count = 0
        self._cum_value = 0
        self._total_hours = 0
        self._total_increment = 0
        self._total_decrement = 0
        self._paused = False
        self._hours_for_count = {}
        # self._log_file = None
        self._keep_history = keep_history
        if keep_history:
            self._history = {}
        self._read_only = None

    @property
    def last_time(self):
        """ Clock time on last observation. """
        return self._last_time

    @property
    def last_count(self):
        """ Count value on last observation. """
        return self._last_count

    @property
    def cum_value(self):
        """ Cumulative count value (integral) on time in unit of hours. """
        return self._cum_value

    @property
    def total_hours(self):
        """ Total working hours since the initial time. """
        return self._total_hours

    @property
    def total_increment(self):
        """ Total number of increment observed. """
        return self._total_increment

    @property
    def total_decrement(self):
        """ Total number of decrement observed. """
        return self._total_decrement

    @property
    def increment_rate(self):
        """ Average number of increment (hourly) on observation period. """
        self.update_to_clock_time()
        try:
            return self._total_increment / self._total_hours
        except ZeroDivisionError:
            return 0

    @property
    def decrement_rate(self):
        """ Average number of decrement (hourly) on observation period. """
        self.update_to_clock_time()
        try:
            return self._total_decrement / self._total_hours
        except ZeroDivisionError:
            return 0

    @property
    def average_count(self):
        """ Average count (hourly) on observation period. """
        self.update_to_clock_time()
        try:
            return self._cum_value / self._total_hours
        except ZeroDivisionError:
            return 0

    @property
    def average_duration(self):
        """ Average timespan (hour) that a load stays in the activity.

        If it is a stationary process,
        i.e., decrement rate == increment rate.
        It is 0 at the initial status,
        i.e., decrement rate is 0 (no decrement observed).

        In original C# version: hours = self.average_count / self.decrement_rate
        """
        self.update_to_clock_time()
        try:
            return self._cum_value / self._total_decrement
        except ZeroDivisionError:
            return 0

    @property
    def working_time_ratio(self):
        """ Ratio value of total working time on observation period. """
        self.update_to_clock_time()
        if self._last_time == self._initial_time:
            return 0
        hours = timedelta2hours(self._last_time - self._initial_time)
        try:
            return self._total_hours / hours
        except ZeroDivisionError:
            return 0

    @property
    def paused(self):
        """ Whether the state is being working. """
        return self._paused

    # @property
    # def log_file(self):
    #     """ File name of log file. """
    #     return self._log_file
    #
    # @log_file.setter
    # def log_file(self, value):
    #     self._log_file = value
    #     if self._log_file is None:
    #         return
    #     str_ = f"Hours, Count, Remark\n" \
    #         f"{self._total_hours}, {self._last_count}, \n"
    #     with os.fdopen(
    #         os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
    #         mode='w', encoding=FileConfig.ENCODING_MODE) as f:
    #         f.write(str_)

    @property
    def keep_history(self):
        """ Whether keep history of each observation. """
        return self._keep_history

    @property
    def history(self):
        """ Scatter points of (time in hours, count) """
        records = None
        if self._keep_history:
            records = [
                (timedelta2hours(key - self._initial_time), self._history[key])
                for key in sorted(self._history)
            ]
        return records

    def update_to_clock_time(self):
        """ Update clock time to be consistent with sandbox. """
        if self._last_time != self._sandbox.clock_time:
            self.observe_count(self._last_count)

    def observe_count(self, count, clock_time=None):
        """ Observe the count value.

        Args:
            count: the observed count value.
            clock_time: the clock time when observation.

        Raises:
            ValueError: an error occurred when time of new count is
                earlier than current time.
        """
        self._check_clock_time(clock_time)
        clock_time = self._sandbox.clock_time
        if clock_time < self._last_time:
            raise ValueError(
                f"Time of new count ({clock_time}) cannot be earlier than "
                f"current time ({self._last_time}).")
        if not self._paused:
            hours = timedelta2hours(clock_time - self._last_time)
            self._total_hours += hours
            self._cum_value += hours * self._last_count
            if count > self._last_count:
                self._total_increment += count - self._last_count
            else:
                self._total_decrement += self._last_count - count
            if self._last_count not in self._hours_for_count:
                self._hours_for_count[self._last_count] = 0
            self._hours_for_count[self._last_count] += hours
        # if self._log_file:
        #     remark = "Paused" if self._paused else ""
        #     str_ = f"{self._total_hours}, {self._last_count}, {remark}\n"
        #     if count != self._last_count:
        #         str_ += f"{self._total_hours}, {count}, {remark}\n"
        #     with os.fdopen(
        #         os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
        #         mode='a', encoding=FileConfig.ENCODING_MODE) as f:
        #         f.write(str_)
        if self._keep_history:
            self._history[clock_time] = count
        self._last_time = clock_time
        self._last_count = count

    def observe_change(self, change, clock_time=None):
        """ Observe the change of the count value.

        Args:
            change: the change of the count value since last observation.
            clock_time: the clock time when observation.
        """
        return self.observe_count(self._last_count + change, clock_time)

    def pause(self, clock_time=None):
        """ Set the state as paused.

        Args:
            clock_time: the clock time when setting.
        """
        if self._paused:
            return
        self._check_clock_time(clock_time)
        self.observe_count(self._last_count, clock_time)
        self._paused = True
        # if self._log_file is None:
        #     return
        # str_ = f"{self._total_hours}, {self._last_count}, Paused\n"
        # with os.fdopen(
        #     os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
        #     mode='a', encoding=FileConfig.ENCODING_MODE) as f:
        #     f.write(str_)

    def resume(self, clock_time):
        """ Restart from the state of paused.

        Args:
            clock_time: the clock time when restart.
        """
        if not self._paused:
            return
        self._check_clock_time(clock_time)
        self._last_time = self._sandbox.clock_time
        self._paused = False
        # if self._log_file is None:
        #     return
        # str_ = f"{self._total_hours}, {self._last_count}, Paused\n" \
        #     f"{self._total_hours}, {self._last_count}, \n"
        # with os.fdopen(
        #     os.open(self._log_file, FileConfig.FLAG, FileConfig.MODE),
        #     mode='a', encoding=FileConfig.ENCODING_MODE) as f:
        #     f.write(str_)

    def warmup(self):
        """ Reset all except the last count. """
        self._initial_time = self._sandbox.clock_time
        self._last_time = self._sandbox.clock_time
        self._cum_value = 0
        self._total_hours = 0
        self._total_increment = 0
        self._total_decrement = 0
        self._hours_for_count = {}

    def percentile(self, ratio):
        """ Get the percentile of count values on time.

        i.e., the count value that with x-percent of time the observation
        is not higher than it.

        Args:
            ratio: values between 0 and 100.

        Returns:
            the percentile of count values on time.
        """
        self._sort_hours_for_count()
        threshold = sum(self._hours_for_count.values()) * ratio / 100
        for key, value in self._hours_for_count.items():
            threshold -= value
            if threshold <= 0:
                return key
        return float('inf')

    def histogram(self, count_interval):
        """ Statistics for the amount of time spent at each range of
        count values.

        Args:
            count_interval: width of the count value interval.

        Returns:
            histogram_: A dictionary mapping from
                (lowerbound value of each interval) to the array of
                [total hours observed, probability, cumulated probability].

        Raises:
            ZeroDivisionError: an error occurred when division by 0.
        """
        self._sort_hours_for_count()
        if len(self._hours_for_count) == 0:
            return {}
        lb2hours = {}
        for count, hours in self._hours_for_count.items():
            count_lb = count // count_interval * count_interval
            if count_lb > 0 and count_lb == count:
                count_lb -= count_interval
            if count_lb not in lb2hours:
                lb2hours[count_lb] = 0
            lb2hours[count_lb] += hours
        hours_sum = sum(lb2hours.values())
        histogram_ = {}
        cum_hours = 0
        for lb, hours in lb2hours.items():
            cum_hours += hours
            try:
                hour_ratio = hours / hours_sum
                cum_hour_ratio = cum_hours / hours_sum
            except ZeroDivisionError as e:
                raise e
            histogram_[lb] = (
                round(hours, 2),
                round(hour_ratio, 2),
                round(cum_hour_ratio, 2),
            )
        return histogram_

    def as_read_only(self):
        """ Return a read-only object of the class instance.

        Returns:
            A read-only hour counter.
        """
        if self._read_only is None or \
            not isinstance(self._read_only, ReadOnlyHourCounter):
            self._read_only = ReadOnlyHourCounter(self)
        return self._read_only

    def _check_clock_time(self, clock_time):
        """ Check whether the clock time is consistent with sandbox.

        Args:
            clock_time: clock time to be checked.

        Raises:
            ValueError: An error occurred when the clock time is not
                consistent with sandbox.
        """
        if clock_time and clock_time != self._sandbox.clock_time:
            raise ValueError("Clock time is not consistent with Sandbox.")

    def _sort_hours_for_count(self):
        """ Sort _hours_for_count by count. """
        dict_ = self._hours_for_count
        self._hours_for_count = {key: dict_[key] for key in sorted(dict_)}
