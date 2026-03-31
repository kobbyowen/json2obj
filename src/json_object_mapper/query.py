import re
from typing import Any, Callable, List, Tuple

QUERY_OPERATORS = ("==", "!=", ">=", "<=", ">", "<")


def tokenize(expr: str) -> List[Any]:
    tokens: List[Any] = []
    index = 0
    source = expr.strip()

    while index < len(source):
        char = source[index]
        if char == ".":
            index += 1
            continue

        if char == "[":
            close = source.find("]", index)
            if close == -1:
                raise ValueError(f"Unclosed bracket in query expression: {expr!r}")
            content = source[index + 1 : close].strip()
            if content == "*":
                tokens.append("*")
            elif content.startswith("?"):
                condition = content[1:].strip()
                if not condition:
                    raise ValueError(f"Empty filter condition in query expression: {expr!r}")
                tokens.append({"filter": condition})
            else:
                try:
                    tokens.append(int(content))
                except ValueError as error:
                    raise ValueError(
                        f"Unsupported bracket token [{content}] in {expr!r}"
                    ) from error
            index = close + 1
            continue

        start = index
        while index < len(source) and source[index] not in ".[":
            index += 1
        name = source[start:index].strip()
        if name:
            tokens.append(name)

    return tokens


def evaluate_query(root: Any, expression: str, wrap: Callable[[Any], Any]) -> List[Any]:
    return evaluate_tokens(root, tokenize(expression), wrap)


def evaluate_tokens(root: Any, tokens: List[Any], wrap: Callable[[Any], Any]) -> List[Any]:
    results: List[Any] = [root]
    for token in tokens:
        next_results: List[Any] = []
        for item in results:
            if isinstance(token, str):
                if token == "*":
                    if isinstance(item, list):
                        next_results.extend(item)
                    elif isinstance(item, dict):
                        next_results.extend(item.values())
                    continue
                if isinstance(item, dict) and token in item:
                    next_results.append(item[token])
                continue

            if isinstance(token, int):
                if isinstance(item, list) and 0 <= token < len(item):
                    next_results.append(item[token])
                continue

            if isinstance(token, dict) and "filter" in token:
                if isinstance(item, list):
                    try:
                        next_results.extend(apply_filter(item, token["filter"]))
                    except ValueError:
                        continue
                continue
        results = next_results

    return [wrap(value) for value in results]


def parse_condition(condition: str) -> Tuple[str, str, Any]:
    text = condition.strip()
    for operator in QUERY_OPERATORS:
        if operator in text:
            left, right = text.split(operator, 1)
            field = left.strip()
            value_text = right.strip()
            if not field or not value_text:
                raise ValueError(f"Invalid filter condition: {condition!r}")
            return field, operator, coerce_condition_value(value_text)
    raise ValueError(f"Unsupported filter condition: {condition!r}")


def coerce_condition_value(value: str) -> Any:
    result: Any = value
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        result = value[1:-1]
    elif re.fullmatch(r"-?\d+", value):
        result = int(value)
    elif re.fullmatch(r"-?\d+\.\d+", value):
        result = float(value)
    else:
        lowered = value.lower()
        if lowered == "true":
            result = True
        elif lowered == "false":
            result = False
        elif lowered == "null":
            result = None
    return result


def compare(left: Any, operator: str, right: Any) -> bool:
    operations = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
    }
    fn = operations.get(operator)
    if fn is None:
        return False
    try:
        return fn(left, right)
    except TypeError:
        return False


def apply_filter(items: List[Any], condition: str) -> List[Any]:
    field, operator, expected = parse_condition(condition)
    matches: List[Any] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if field not in item:
            continue
        if compare(item[field], operator, expected):
            matches.append(item)
    return matches
