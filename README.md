# json2obj

**`json2obj`** is a lightweight Python library that lets you interact with JSON data using **attribute-style access** instead of dictionary keys.

It turns JSON objects into `JSONObjectMapper` instances that feel natural to use in Python code, while preserving full JSON compatibility.

```python
from json2obj import JSONObjectMapper

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
- Read-only mode (immutability enforced)
- Dot/bracket path lookups (`obj.get_path("a.b[0].c")`)
- **New:** `set_path()` / `del_path()` for dot paths
- **New:** `default_factory` + `autocreate_missing` for safe defaults
- Utility methods: `to_dict`, `to_json`, `from_json`, `merge`

## Install

```bash
pip install json2obj
```

from json2obj import JSONObjectMapper, JSONAccessError

# 1) Wrap & read (basic)

obj = JSONObjectMapper({"user": {"name": "Kobby", "age": 29}})
assert obj.user.name == "Kobby"
assert obj.user.age == 29

# 2) Write with dot notation

obj.user.country = "GH"
assert obj.user.country == "GH"

# 3) Lists of dicts (read & write via attribute access)

obj.services = [{}] # start with a list containing one dict
obj.services[0].name = "auth" # item is wrapped → dot works
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
cfg.profile.settings.theme = "dark" # on-demand creation of nested dicts
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

````

## Tests

```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
````

MIT License.
