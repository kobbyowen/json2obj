import re
from typing import Any, Callable, List, Optional


def is_identifier(key: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key))


PATH_TOKEN = re.compile(
    r"""
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)     # identifier
    | \[ (?P<index>\d+) \]               # [index]
""",
    re.VERBOSE,
)


def ensure_list_length(lst: List[Any], index: int) -> None:
    if index >= len(lst):
        lst.extend([None] * (index + 1 - len(lst)))


def parse_path_tokens(path: str):
    return list(PATH_TOKEN.finditer(path.replace(".", " ")))


def is_last(current_index: int, tokens: List[Any]) -> bool:
    return current_index == len(tokens) - 1


def peek_is_index(tokens: List[Any], current_index: int) -> bool:
    return tokens[current_index + 1].group("index") is not None


def expect_dict(obj: Any, context: str):
    if not isinstance(obj, dict):
        raise TypeError(f"Expected dict {context}")


def expect_list(obj: Any, context: str):
    if not isinstance(obj, list):
        raise TypeError(f"Expected list {context}")


def get_token_value(container: Any, token):
    name, index = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"before '{name}'")
        return container[name]
    expect_list(container, f"before index [{index}]")
    return container[int(index)]


def assign_at(container: Any, token, value: Any, create_parents: bool, path: str):
    name, index = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"in '{path}'")
        container[name] = value
        return
    expect_list(container, f"in '{path}'")
    index_int = int(index)
    if index_int >= len(container) and not create_parents:
        raise IndexError(f"Index {index_int} out of range in '{path}'")
    ensure_list_length(container, index_int)
    container[index_int] = value


def ensure_next(container: Any, token, next_is_index: bool, create_parents: bool, path: str):
    name, index = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"in '{path}'")
        next_value = container.get(name)
        if next_value is None:
            if not create_parents:
                raise KeyError(f"Missing key '{name}' in '{path}'")
            container[name] = [] if next_is_index else {}
            next_value = container[name]
        return next_value
    expect_list(container, f"in '{path}'")
    index_int = int(index)
    if index_int >= len(container):
        if not create_parents:
            raise IndexError(f"Index {index_int} out of range in '{path}'")
        ensure_list_length(container, index_int)
        container[index_int] = [] if next_is_index else {}
    return container[index_int]


def traverse_parent(root: Any, tokens: List[Any], path: str, strict: bool):
    current = root
    for _, token in enumerate(tokens[:-1]):
        try:
            current = get_token_value(current, token)
        except Exception:
            if strict:
                segment = token.group("name") or f"[{token.group('index')}]"
                raise KeyError(f"Missing segment before end at '{segment}' in '{path}'") from None
            return None
    return current


def delete_on_parent(parent: Any, last_token, strict: bool):
    name, index = last_token.group("name"), last_token.group("index")
    if name is not None:
        expect_dict(parent, "for deletion")
        if name in parent:
            del parent[name]
        elif strict:
            raise KeyError(f"Missing key '{name}'")
        return
    expect_list(parent, "for deletion")
    index_int = int(index)
    if 0 <= index_int < len(parent):
        parent.pop(index_int)
    elif strict:
        raise IndexError(f"Index {index_int} out of range")


def wrap_value(
    value: Any,
    readonly: bool,
    default_factory: Optional[Callable[[], Any]],
    autocreate_missing: bool,
    factory_object: type,
) -> Any:
    if isinstance(value, dict):
        return factory_object(
            value,
            readonly=readonly,
            default_factory=default_factory,
            autocreate_missing=autocreate_missing,
            _no_copy=True,
        )
    if isinstance(value, list):
        return [
            (
                wrap_value(item, readonly, default_factory, autocreate_missing, factory_object)
                if isinstance(item, (dict, list))
                else item
            )
            for item in value
        ]
    return value
