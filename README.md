# json-object-mapper

**`json-object-mapper`** is a lightweight Python library that lets you interact with JSON data using **attribute-style access** instead of dictionary keys.

The PyPI distribution is published as `json-object-mapper`.

It turns JSON objects into `JSONObjectMapper` instances that feel natural to use in Python code, while preserving full JSON compatibility.

```python
from json_object_mapper import JSONObjectMapper

data = {
    "user": {"name": "Kobby", "age": 29, "skills": ["python", "aws", "forex"]}
}
obj = JSONObjectMapper(data)
print(obj.user.name)        # "Kobby"
print(obj.user.skills[0])   # "python"
print(obj.to_json(indent=2))
```

## ✨ Features

- Attribute-style access (`obj.key`) for dict keys
- Recursive wrapping for nested dicts and lists
- Query engine (`query`, `exists`, `count`, `compile`) with wildcard and filter support
- ORM-like list helpers via `QueryableList` (`filter`, `get`, `first`, `last`, `count`)
- Read-only mode (immutability enforced)
- Dot/bracket path lookups (`obj.get_path("a.b[0].c")`)
- **New:** `set_path()` / `del_path()` for dot paths
- **New:** `default_factory` + `autocreate_missing` for safe defaults
- Utility methods: `to_dict`, `to_json`, `from_json`, `merge`

## Release Notes

### v2.1.0

- Renamed import path to `json_object_mapper` and aligned package metadata for the new distribution name.
- Added JSONPath-like query API:
  - `obj.query(expression, first=False, default=None)`
  - `obj.exists(expression)`
  - `obj.count(expression)`
  - `obj.compile(expression)`
- Implemented query features: property access, nested access, list indexing, wildcards, nested wildcard flattening, and basic filters (`==`, `!=`, `>`, `<`, `>=`, `<=`).
- Isolated query implementation into a dedicated module for maintainability.
- Added ORM-style list querying through `QueryableList`:
  - `filter(...)`, `get(...)`, `first()`, `last()`, `count()`
  - Supports nested field filters such as `profile__age__gt=20`.
- Expanded test coverage significantly across mapper, query parser, query engine, and queryable list behavior (including deep nested JSON scenarios and edge cases).
- Added strict type-checking support:
  - mypy configuration in project metadata
  - `py.typed` marker for typed package support
  - type fixes in mapper and queryable helpers
- CI improvements:
  - Ruff linting
  - mypy checks
  - multi-version unit tests
  - build and package validation
- Publishing workflow configured for PyPI release automation.

## Install

```bash
pip install json-object-mapper
```

## Usage

```python
from json_object_mapper import JSONObjectMapper, JSONAccessError

# 1) Wrap & read (basic)
obj = JSONObjectMapper({"user": {"name": "Kobby", "age": 29}})
assert obj.user.name == "Kobby"
assert obj.user.age == 29

# 2) Write with dot notation
obj.user.country = "GH"
assert obj.user.country == "GH"

# 3) Lists of dicts (read & write via attribute access)
obj.services = [{}]  # start with a list containing one dict
obj.services[0].name = "auth"  # item is wrapped → dot works
obj.services[0].enabled = True
assert obj.services[0].name == "auth"
assert obj.services[0].enabled is True

# 4) Non-identifier keys (use mapping-style access)
# Keys like "first-name" can't be attributes; use get()/[] instead
obj.meta = {"first-name": "Kobby"}
assert obj.meta.get("first-name") == "Kobby"
assert obj.meta["first-name"] == "Kobby"
# getattr(obj.meta, "first-name") would raise JSONAccessError

# 5) Safe defaults + auto-create (no extra helpers required)
# Missing attributes produce defaults; with autocreate they persist.
cfg = JSONObjectMapper({}, default_factory=dict, autocreate_missing=True)
cfg.profile.settings.theme = "dark"  # on-demand creation of nested dicts
assert cfg.profile.settings.theme == "dark"

# 6) Merge convenience (shallow merge into root dict)
cfg.merge({"features": {"beta": True}})
assert cfg.features.beta is True

# 7) Read-only wrappers (safe reads; writes raise)
ro = JSONObjectMapper({"debug": True}, readonly=True)
assert ro.debug is True
try:
    ro.debug = False
    raise AssertionError("should not be able to write in readonly mode")
except AttributeError:
    pass
```

## Tests

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
venv/bin/ruff check .
venv/bin/mypy .
```

## Publishing

Publishing is automated with GitHub Actions using PyPI trusted publishing. Create a GitHub release after configuring the `pypi` environment in the repository settings.

MIT License.
