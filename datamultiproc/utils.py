import logging
from typing import Union, Optional, Any


def get_class_name(obj: Union[str, type, object]):
    if obj is None or isinstance(obj, str):
        return obj

    if isinstance(obj, type):
        return obj.__name__

    return obj.__class__.__name__


def get_class_path(name_class_or_object: Optional[Union[str, Any]] = None):
    if not name_class_or_object:
        return None

    if isinstance(name_class_or_object, str):
        return name_class_or_object

    if isinstance(name_class_or_object, type):
        return f"{name_class_or_object.__module__}.{name_class_or_object.__name__}"

    return (
        f"{name_class_or_object.__module__}.{name_class_or_object.__class__.__name__}"
    )


def get_logger(name_class_or_object: Optional[Union[str, Any]] = None):
    if not name_class_or_object:
        return logging.getLogger()

    return logging.getLogger(get_class_path(name_class_or_object))


class LoggerMixin:
    logger = property(get_logger)
