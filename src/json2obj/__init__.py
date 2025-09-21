"""json2obj public interface."""

from .core import JSONObjectMapper
from .exceptions import JSONAccessError

__all__ = ["JSONAccessError", "JSONObjectMapper"]
