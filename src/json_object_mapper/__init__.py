"""json_object_mapper public interface."""

from .core import JSONObjectMapper
from .exceptions import JSONAccessError

__all__ = ["JSONAccessError", "JSONObjectMapper"]
