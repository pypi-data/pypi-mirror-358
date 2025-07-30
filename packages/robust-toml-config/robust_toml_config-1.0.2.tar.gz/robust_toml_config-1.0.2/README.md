# Robust TOML Config Manager

[![PyPI version](https://img.shields.io/pypi/v/robust-toml-config.svg)](https://pypi.org/project/robust-toml-config/)
[![Python versions](https://img.shields.io/pypi/pyversions/robust-toml-config.svg)](https://pypi.org/project/robust-toml-config/)

A robust, feature-rich TOML configuration manager for Python that preserves 
formatting, comments, and ordering in your TOML files.

## Features

- ✅ **Format Preservation**: Maintains comments, whitespace, and ordering
- 🛡️ **Robust Handling**: Automatic encoding fallback and error recovery
- ⚙️ **Dot-Path Access**: Simple `get("section.key")` and `set("section.key", value)` syntax
- 💾 **Auto-Save**: Changes automatically saved to disk (configurable)
- 🔄 **Batch Updates**: Context manager for efficient batch operations
- 🧪 **Type Safety**: Ensure values are of the correct type
- 📦 **Lightweight**: Single dependency (tomlkit)

## Installation

```bash
pip install robust-toml-config
```

## Quick Start

```python
from robust_toml_config import TOMLConfig

# Create or load config
config = TOMLConfig(
    "config.toml",
    default_data={
        "app": {
            "name": "My App",
            "version": "1.0.0"
        }
    }
)

# Get values
app_name = config.get("app.name")  # "My App"

# Set values
config.set("app.version", "1.0.1")

# Update entire section
config.update_section("database", {
    "host": "db.example.com",
    "port": 5432
})

# Batch updates
with config.batch_update():
    config.set("logging.level", "DEBUG")
    config.set("logging.file", "app.log")
    config.set("server.port", 8080)

# Ensure type safety
timeout = config.ensure_type("server.timeout", float, 30.0)

# Save to a new file
config.save("config_backup.toml")
```

## Documentation

Full documentation available at [GitHub Wiki](https://github.com/yourusername/robust-toml-config/wiki)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.