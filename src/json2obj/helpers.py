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


def is_last(i: int, toks: List[Any]) -> bool:
    return i == len(toks) - 1


def peek_is_index(toks: List[Any], i: int) -> bool:
    return toks[i + 1].group("index") is not None


def expect_dict(obj: Any, ctx: str):
    if not isinstance(obj, dict):
        raise TypeError(f"Expected dict {ctx}")


def expect_list(obj: Any, ctx: str):
    if not isinstance(obj, list):
        raise TypeError(f"Expected list {ctx}")


def get_token_value(container: Any, token):
    name, idx = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"before '{name}'")
        return container[name]
    expect_list(container, f"before index [{idx}]")
    return container[int(idx)]


def assign_at(container: Any, token, value: Any, create_parents: bool, path: str):
    name, idx = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"in '{path}'")
        container[name] = value
        return
    expect_list(container, f"in '{path}'")
    i = int(idx)
    if i >= len(container) and not create_parents:
        raise IndexError(f"Index {i} out of range in '{path}'")
    ensure_list_length(container, i)
    container[i] = value


def ensure_next(container: Any, token, next_is_index: bool, create_parents: bool, path: str):
    name, idx = token.group("name"), token.group("index")
    if name is not None:
        expect_dict(container, f"in '{path}'")
        nxt = container.get(name)
        if nxt is None:
            if not create_parents:
                raise KeyError(f"Missing key '{name}' in '{path}'")
            container[name] = [] if next_is_index else {}
            nxt = container[name]
        return nxt
    expect_list(container, f"in '{path}'")
    i = int(idx)
    if i >= len(container):
        if not create_parents:
            raise IndexError(f"Index {i} out of range in '{path}'")
        ensure_list_length(container, i)
        container[i] = [] if next_is_index else {}
    return container[i]


def traverse_parent(root: Any, toks: List[Any], path: str, strict: bool):
    cur = root
    for _, tok in enumerate(toks[:-1]):
        try:
            cur = get_token_value(cur, tok)
        except Exception:
            if strict:
                seg = tok.group("name") or f"[{tok.group('index')}]"
                raise KeyError(f"Missing segment before end at '{seg}' in '{path}'") from None
            return None
    return cur


def delete_on_parent(parent: Any, last_token, strict: bool):
    name, idx = last_token.group("name"), last_token.group("index")
    if name is not None:
        expect_dict(parent, "for deletion")
        if name in parent:
            del parent[name]
        elif strict:
            raise KeyError(f"Missing key '{name}'")
        return
    expect_list(parent, "for deletion")
    i = int(idx)
    if 0 <= i < len(parent):
        parent.pop(i)
    elif strict:
        raise IndexError(f"Index {i} out of range")


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
                wrap_value(v, readonly, default_factory, autocreate_missing, factory_object)
                if isinstance(v, (dict, list))
                else v
            )
            for v in value
        ]
    return value
