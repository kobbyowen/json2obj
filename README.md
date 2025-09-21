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

## Quick Start
```python
from json2obj import JSONObjectMapper

# Defaults + auto-create
cfg = JSONObjectMapper({}, default_factory=dict, autocreate_missing=True)
cfg.profile.settings.theme = "dark"
assert cfg.get_path("profile.settings.theme") == "dark"

# Path editing
cfg.set_path("services[0].name", "auth").set_path("services[0].enabled", True)
cfg.del_path("services[0].name")
```

## Tests
```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
```

MIT License.
