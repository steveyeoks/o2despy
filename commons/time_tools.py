import datetime as dt
import time


def timedelta2hours(timedelta):
    """ Convert datetime.timedelta to total hours.

    Args:
        timedelta: datetime.timedelta.

    Returns:
        total hours.

    Raises:
        ZeroDivisionError: an error occurred when division by 0.
    """
    try:
        return timedelta.total_seconds() / float(3600)
    except ZeroDivisionError as e:
        raise e


def timedelta_to_str(timedelta):
    """ Convert datetime.timedelta to a string.

    Args:
        timedelta: datetime.timedelta.

    Returns:
        a string in format of HH:MM:SS.
    """
    total_seconds = timedelta.total_seconds()
    hours = int(total_seconds / 3600)
    minutes = int((total_seconds - hours * 3600) // 60)
    seconds = int(total_seconds - hours * 3600 - minutes * 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{hours}:{minutes}:{seconds}"


def dbstr_time_to_unix(str_d):
    """ Convert time string to unix timestamp.

    Args:
        str_d: a time string with format like 20191116150225.

    Returns:
        unix seconds.
    """
    date_object = dt.datetime.strptime(str_d, '%Y%m%d%H%M%S')
    return int(time.mktime(date_object.timetuple()))


def unix2datetime(timestamp):
    """ Convert unix timestamp to datetime.

    Args:
        timestamp: unix seconds like 1573870200.

    Returns:
        datetime.datetime.
    """
    return dt.datetime.fromtimestamp(timestamp)


def datetime_to_unix(d):
    """ Convert datetime to unix seconds.

    Args:
        d: datetime.datetime.

    Returns:
        unix seconds.
    """
    return int(time.mktime(d.timetuple()))
