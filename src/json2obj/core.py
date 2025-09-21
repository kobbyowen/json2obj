import copy
import json
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

from .exceptions import JSONAccessError
from .helpers import (
    assign_at,
    delete_on_parent,
    ensure_next,
    is_identifier,
    is_last,
    parse_path_tokens,
    peek_is_index,
    traverse_parent,
    wrap_value,
)

JSONScalar = Union[str, int, float, bool, None]
JSONType = Union[JSONScalar, "JSONObjectMapper", List["JSONObjectMapper"], Dict[str, Any]]


class JSONObjectMapper:
    __slots__ = ("__autocreate_missing", "__default_factory", "__json", "__readonly")

    def __init__(
        self,
        data: Union[str, bytes, bytearray, Mapping[str, Any], MutableMapping[str, Any], List[Any]],
        *,
        readonly: bool = False,
        default_factory: Optional[Callable[[], Any]] = None,
        autocreate_missing: bool = False,
        _no_copy: bool = False,
    ) -> None:
        self.__json = (
            json.loads(data)
            if isinstance(data, (str, bytes, bytearray))
            else (data if _no_copy else copy.deepcopy(data))
        )
        if not isinstance(self.__json, (dict, list)):
            raise TypeError("JSONObjectMapper must wrap a dict or list (or JSON string thereof).")
        self.__readonly = bool(readonly)
        self.__default_factory = default_factory
        self.__autocreate_missing = bool(autocreate_missing)

    def __repr__(self) -> str:  # pragma: no cover
        return f"JSONObjectMapper(readonly={self.__readonly}, data={self.__json!r})"

    def to_dict(self) -> Any:
        return copy.deepcopy(self.__json)

    def to_json(self, *, indent: Optional[int] = None, sort_keys: bool = False) -> str:
        return json.dumps(self.__json, indent=indent, sort_keys=sort_keys)

    @classmethod
    def from_json(cls, json_string: Union[str, bytes, bytearray], *, readonly: bool = False) -> "JSONObjectMapper":
        return cls(json_string, readonly=readonly)

    def readonly(self) -> bool:
        return self.__readonly

    # ---------------------------- attribute access ----------------------------

    def __getattr__(self, attribute_name: str) -> Any:
        data = object.__getattribute__(self, "_JSONObjectMapper__json")
        if isinstance(data, list):
            raise JSONAccessError(f"Cannot access attribute '{attribute_name}' on list")
        if attribute_name in type(self).__dict__:
            return object.__getattribute__(self, attribute_name)
        if not is_identifier(attribute_name):
            raise JSONAccessError(f"'{attribute_name}' is not a valid attribute identifier")
        try:
            value = data[attribute_name]
        except KeyError as error:
            value = self._on_missing_attr(data, attribute_name, error)
        return self._wrap(value)

    def _on_missing_attr(self, data: dict, attribute_name: str, error: Exception) -> Any:
        factory = object.__getattribute__(self, "_JSONObjectMapper__default_factory")
        readonly_flag = object.__getattribute__(self, "_JSONObjectMapper__readonly")
        autocreate_flag = object.__getattribute__(self, "_JSONObjectMapper__autocreate_missing")
        if factory is None:
            raise JSONAccessError(f"'{attribute_name}' not found") from error
        produced = factory()
        if autocreate_flag and not readonly_flag:
            data[attribute_name] = produced
        return produced

    def _wrap(self, value: Any) -> Any:
        readonly_flag = object.__getattribute__(self, "_JSONObjectMapper__readonly")
        default_factory = object.__getattribute__(self, "_JSONObjectMapper__default_factory")
        autocreate_flag = object.__getattribute__(self, "_JSONObjectMapper__autocreate_missing")
        return wrap_value(value, readonly_flag, default_factory, autocreate_flag, factory_object=self.__class__)

    def __setattr__(self, attribute_name: str, value: Any) -> None:
        if attribute_name in {
            "_JSONObjectMapper__json",
            "_JSONObjectMapper__readonly",
            "_JSONObjectMapper__default_factory",
            "_JSONObjectMapper__autocreate_missing",
        }:
            return object.__setattr__(self, attribute_name, value)
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        if isinstance(self.__json, list):
            raise AttributeError("Cannot set attributes on a list")
        if not is_identifier(attribute_name):
            raise AttributeError(f"'{attribute_name}' is not a valid attribute name")
        self.__json[attribute_name] = value

    # ----------------------------- mapping access -----------------------------

    def __getitem__(self, key: Union[int, str]) -> Any:
        try:
            value = self.__json[key]  # type: ignore[index]
        except Exception as error:
            raise KeyError(key) from error
        return self._wrap(value)

    def __setitem__(self, key: Union[int, str], value: Any) -> None:
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        self.__json[key] = value  # type: ignore[index]

    def __iter__(self) -> Iterator:
        return iter(self.__json)

    def __len__(self) -> int:
        return len(self.__json)

    def get(self, key: Union[str, int], default: Any = None) -> Any:
        try:
            value = self.__json[key]  # type: ignore[index]
        except Exception:
            return default
        return self._wrap(value)

    def keys(self) -> Iterable:
        if isinstance(self.__json, dict):
            return self.__json.keys()
        raise TypeError("keys() only valid for dict roots")

    def items(self) -> Iterable[Tuple[Any, Any]]:
        if isinstance(self.__json, dict):
            return ((key, self._wrap(value)) for key, value in self.__json.items())
        raise TypeError("items() only valid for dict roots")

    def values(self) -> Iterable[Any]:
        if isinstance(self.__json, dict):
            return (self._wrap(value) for value in self.__json.values())
        raise TypeError("values() only valid for dict roots")

    # -------------------------------- path ops --------------------------------

    def get_path(self, path: str, default: Any = None) -> Any:
        current: Any = self
        for token in parse_path_tokens(path):
            try:
                current = (
                    getattr(current, token.group("name"))
                    if token.group("name")
                    else current[int(token.group("index"))]
                )
            except Exception:
                return default
        return current

    def set_path(self, path: str, value: Any, *, create_parents: bool = True) -> "JSONObjectMapper":
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        tokens = parse_path_tokens(path)
        if not tokens:
            raise ValueError("Empty path")
        current = self.__json
        for index, token in enumerate(tokens):
            if is_last(index, tokens):
                assign_at(current, token, value, create_parents, path)
                return self
            current = ensure_next(current, token, peek_is_index(tokens, index), create_parents, path)
        return self

    def del_path(self, path: str, *, raise_on_missing: bool = False) -> "JSONObjectMapper":
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        tokens = parse_path_tokens(path)
        if not tokens:
            raise ValueError("Empty path")
        parent = traverse_parent(self.__json, tokens, path, raise_on_missing)
        if parent is None:
            return self
        delete_on_parent(parent, tokens[-1], raise_on_missing)
        return self

    # --------------------------------- merge ----------------------------------

    def merge(self, other: Mapping[str, Any]) -> "JSONObjectMapper":
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        if not isinstance(self.__json, dict):
            raise TypeError("merge() requires a dict root")
        for key, value in other.items():
            self.__json[key] = value
        return self
