from typing import Any, Dict, Iterable

OPS = {"eq", "ne", "gt", "lt", "gte", "lte"}
_COUNT_SENTINEL = object()


class QueryableList(list):
    """List wrapper with ORM-like helper methods."""

    def __init__(self, data: Iterable[Any]):
        super().__init__(data)

    def filter(self, **conditions: Any) -> "QueryableList":
        results = [item for item in self if _matches(item, conditions)]
        return QueryableList(results)

    def get(self, **conditions: Any) -> Any:
        results = self.filter(**conditions)
        if len(results) == 0:
            raise ValueError("No matching item found")
        if len(results) > 1:
            raise ValueError("Multiple items found")
        return results[0]

    def first(self) -> Any:
        return self[0] if self else None

    def last(self) -> Any:
        return self[-1] if self else None

    def count(self, value: Any = _COUNT_SENTINEL, /) -> int:
        if value is _COUNT_SENTINEL:
            return len(self)
        return super().count(value)


def _matches(item: Any, conditions: Dict[str, Any]) -> bool:
    for key, expected in conditions.items():
        field_parts = key.split("__")
        if len(field_parts) > 1 and field_parts[-1] in OPS:
            op = field_parts[-1]
            field_path = "__".join(field_parts[:-1])
        else:
            op = "eq"
            field_path = key

        actual = _get_nested_attr(item, field_path)
        if not _compare(actual, op, expected):
            return False
    return True


def _get_nested_attr(obj: Any, path: str) -> Any:
    value = obj
    for part in path.split("__"):
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(part)
            continue
        value = getattr(value, part, None)
    return value


def _compare(a: Any, op: str, b: Any) -> bool:
    operations = {
        "eq": lambda left, right: left == right,
        "ne": lambda left, right: left != right,
        "gt": lambda left, right: left > right,
        "lt": lambda left, right: left < right,
        "gte": lambda left, right: left >= right,
        "lte": lambda left, right: left <= right,
    }
    fn = operations.get(op)
    if fn is None:
        return False
    try:
        return fn(a, b)
    except TypeError:
        return False
