## 🚀 Version 2 Features

### 1. Typed Models (Schema Support)

Define structured models with built-in type validation and optional coercion.

```python
class User(JSONObjectMapper):
    name: str
    age: int
```

---

### 2. Query Engine

Query JSON data using expressive, JSONPath-like syntax.

```python
obj.query("users[*].name")
obj.query("orders[?price > 100].id")
```

---

### 3. Change Tracking

Automatically track all modifications to your data.

```python
obj.user.name = "New Name"
obj.changes()
```

---

### 4. Undo / Redo Support

Revert or reapply changes seamlessly.

```python
obj.undo()
obj.redo()
```

---

### 5. Reactive Watchers

Subscribe to changes and react in real-time.

```python
obj.watch("user.name", callback)
```

---

### 6. Smart Merge Strategies

Advanced merging with configurable conflict resolution.

```python
obj.merge(data, strategy="deep")
```

---

### 7. Serialization Hooks

Transform data dynamically during export.

```python
obj.to_json(transform={"user.password": lambda _: "***"})
```

---

### 8. Schema Generation

Automatically infer schema from JSON data.

```python
obj.schema()
```

---

### 9. Lazy Loading Mode

Improve performance by wrapping objects only when accessed.

```python
JSONObjectMapper(data, lazy=True)
```

---

### 10. ORM-like Query Helpers

Filter and retrieve data using intuitive query patterns.

```python
obj.users.filter(age__gt=18)
obj.users.get(name="Kobby")
```

---

### 11. Field-Level Permissions

Control access and visibility of specific fields.

```python
JSONObjectMapper(data, permissions={"user.password": "readonly"})
```

---

### 12. Plugin System

Extend functionality with custom plugins.

```python
obj.use(MyPlugin())
```

---

### 13. File Binding

Bind JSON directly to files with optional auto-save.

```python
JSONObjectMapper.bind("config.json", autosave=True)
```

---

### 14. API Integration

Load and interact with remote JSON APIs.

```python
JSONObjectMapper.from_api(url)
```

---

### 15. Enhanced Error Handling

Clear, contextual error messages for faster debugging.

---

### 16. AI / LLM Utilities

Built-in helpers for AI workflows and prompt generation.

```python
obj.to_prompt()
obj.ask("...")
```
