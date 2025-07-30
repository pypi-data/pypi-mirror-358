# 🔧 ConfigFlow

**ConfigFlow** is a Python library for managing configuration files with real-time monitoring and event-driven updates.  
Supports **JSON**, **YAML**, and more — with validation and a simple API.

---

## ✨ Features

- **Unified Parsing**: Load JSON, YAML, and other formats.
- **Real-Time Monitoring**: Detect config changes instantly using `watchdog`.
- **Event-Driven**: Register callbacks for config updates.
- **Validation**: Ensure configs match your schema with `pydantic`.

---

## 📦 Installation

```bash
pip install configflow
```

---

## ⚡ Quickstart

```python
from configflow import ConfigFlow

# Initialize with a config file
config = ConfigFlow("settings.yaml")

# Define a schema
schema = {"port": int, "debug": bool}

# Register a callback
@config.on_change
def handle_update(changed_config):
    print(f"Config updated: {changed_config}")

# Load and watch
config.load(schema=schema)
config.watch()

# Keep running (Ctrl+C to stop)
try:
    while True:
        pass
except KeyboardInterrupt:
    config.stop()
```

---

## 📝 Example Config (`settings.yaml`)

```yaml
port: 8080
debug: true
```

---

## 📚 Documentation

Full documentation is available at **[ConfigFlow Docs](https://configflow.readthedocs.io)**.  
(*Replace `#` with your actual docs link once published.*)

---

## 🤝 Contributing

We welcome contributions!  
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on adding new features, bug fixes, or parser support.

---

## 📄 License

**MIT License**

> Includes dependencies with compatible licenses:
> - [`watchdog`](https://github.com/gorakhargosh/watchdog) — Apache 2.0  
> - [`PyYAML`](https://pyyaml.org/) — MIT  
> - [`orjson`](https://github.com/ijl/orjson) — Apache 2.0 / MIT  
> - [`pydantic`](https://docs.pydantic.dev/) — MIT  
