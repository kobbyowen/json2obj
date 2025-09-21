from __future__ import annotations

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
        data: (str | bytes | bytearray | Mapping[str, Any] | MutableMapping[str, Any] | list[Any]),
        *,
        readonly: bool = False,
        default_factory: Callable[[], Any] | None = None,
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

    def to_json(self, *, indent: int | None = None, sort_keys: bool = False) -> str:
        return json.dumps(self.__json, indent=indent, sort_keys=sort_keys)

    @classmethod
    def from_json(cls, s: str | bytes | bytearray, *, readonly: bool = False) -> JSONObjectMapper:
        return cls(s, readonly=readonly)

    def readonly(self) -> bool:
        return self.__readonly

    # ---------------------------- attribute access ----------------------------

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_JSONObjectMapper__json")
        if isinstance(data, list):
            raise JSONAccessError(f"Cannot access attribute '{name}' on list")
        if name in type(self).__dict__:
            return object.__getattribute__(self, name)
        if not is_identifier(name):
            raise JSONAccessError(f"'{name}' is not a valid attribute identifier")
        try:
            value = data[name]
        except KeyError as e:
            value = self._on_missing_attr(data, name, e)
        return self._wrap(value)

    def _on_missing_attr(self, data: dict, name: str, err: Exception) -> Any:
        factory = object.__getattribute__(self, "_JSONObjectMapper__default_factory")
        ro = object.__getattribute__(self, "_JSONObjectMapper__readonly")
        auto = object.__getattribute__(self, "_JSONObjectMapper__autocreate_missing")
        if factory is None:
            raise JSONAccessError(f"'{name}' not found") from err
        produced = factory()
        if auto and not ro:
            data[name] = produced
        return produced

    def _wrap(self, value: Any) -> Any:
        ro = object.__getattribute__(self, "_JSONObjectMapper__readonly")
        fac = object.__getattribute__(self, "_JSONObjectMapper__default_factory")
        auto = object.__getattribute__(self, "_JSONObjectMapper__autocreate_missing")
        return wrap_value(value, ro, fac, auto, factory_object=self.__class__)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {
            "_JSONObjectMapper__json",
            "_JSONObjectMapper__readonly",
            "_JSONObjectMapper__default_factory",
            "_JSONObjectMapper__autocreate_missing",
        }:
            return object.__setattr__(self, name, value)
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        if isinstance(self.__json, list):
            raise AttributeError("Cannot set attributes on a list")
        if not is_identifier(name):
            raise AttributeError(f"'{name}' is not a valid attribute name")
        self.__json[name] = value

    # ----------------------------- mapping access -----------------------------

    def __getitem__(self, key: int | str) -> Any:
        try:
            value = self.__json[key]  # type: ignore[index]
        except Exception as e:
            raise KeyError(key) from e
        return self._wrap(value)

    def __setitem__(self, key: int | str, value: Any) -> None:
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        self.__json[key] = value  # type: ignore[index]

    def __iter__(self) -> Iterator:
        return iter(self.__json)

    def __len__(self) -> int:
        return len(self.__json)

    def get(self, key: str | int, default: Any = None) -> Any:
        try:
            value = self.__json[key]  # type: ignore[index]
        except Exception:
            return default
        return self._wrap(value)

    def keys(self) -> Iterable:
        if isinstance(self.__json, dict):
            return self.__json.keys()
        raise TypeError("keys() only valid for dict roots")

    def items(self) -> Iterable[tuple[Any, Any]]:
        if isinstance(self.__json, dict):
            return ((k, self._wrap(v)) for k, v in self.__json.items())
        raise TypeError("items() only valid for dict roots")

    def values(self) -> Iterable[Any]:
        if isinstance(self.__json, dict):
            return (self._wrap(v) for v in self.__json.values())
        raise TypeError("values() only valid for dict roots")

    # -------------------------------- path ops --------------------------------

    def get_path(self, path: str, default: Any = None) -> Any:
        cur: Any = self
        for tok in parse_path_tokens(path):
            try:
                cur = (
                    getattr(cur, tok.group("name"))
                    if tok.group("name")
                    else cur[int(tok.group("index"))]
                )
            except Exception:
                return default
        return cur

    def set_path(self, path: str, value: Any, *, create_parents: bool = True) -> JSONObjectMapper:
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        toks = parse_path_tokens(path)
        if not toks:
            raise ValueError("Empty path")
        cur = self.__json
        for i, tok in enumerate(toks):
            if is_last(i, toks):
                assign_at(cur, tok, value, create_parents, path)
                return self
            cur = ensure_next(cur, tok, peek_is_index(toks, i), create_parents, path)
        return self

    def del_path(self, path: str, *, raise_on_missing: bool = False) -> JSONObjectMapper:
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        toks = parse_path_tokens(path)
        if not toks:
            raise ValueError("Empty path")
        parent = traverse_parent(self.__json, toks, path, raise_on_missing)
        if parent is None:
            return self
        delete_on_parent(parent, toks[-1], raise_on_missing)
        return self

    # --------------------------------- merge ----------------------------------

    def merge(self, other: Mapping[str, Any]) -> JSONObjectMapper:
        if self.__readonly:
            raise AttributeError("Mapper is read-only")
        if not isinstance(self.__json, dict):
            raise TypeError("merge() requires a dict root")
        for k, v in other.items():
            self.__json[k] = v
        return self
