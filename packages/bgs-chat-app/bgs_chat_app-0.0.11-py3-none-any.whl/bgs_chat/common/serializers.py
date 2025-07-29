import datetime
from typing import Optional


DATE_TIME_FORMAT = '%d-%m-%y %H:%M:%S.%f%z'


def serialize_datetime(passed_datetime: Optional[datetime.datetime]) -> Optional[str]:
    """
    Serialize a datetime instance, which may be None, to a string representation
    If datetime is None, None is returned
    """

    if isinstance(passed_datetime, datetime.datetime):
        return passed_datetime.strftime(DATE_TIME_FORMAT)
    return None


def deserialize_datetime(str_datetime: Optional[str]) -> Optional[datetime.datetime]:
    """
    Deserializes a string of a date to a datetime format
    if str_datetime is 'falsy', a value of None is returned
    """
    if not str_datetime:
        return None

    return datetime.datetime.strptime(str_datetime, DATE_TIME_FORMAT)