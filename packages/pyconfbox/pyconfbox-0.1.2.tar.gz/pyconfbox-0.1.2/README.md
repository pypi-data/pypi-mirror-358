# PyConfBox 🎯

**Python Configuration Management with Multiple Storage Backends**

PyConfBox is a powerful Python configuration management library that provides unified management of environment variables, system variables, global variables, and more.

> **한국어 문서**: [README_ko.md](README_ko.md) | **English Documentation**: README.md (current)

## ✨ Key Features

- **🏗️ Multiple Storage Backends**: Memory, Environment, File (JSON/YAML/TOML), SQLite, Redis
- **🎯 Scope System**: Support for env, global, local, system, secret, django scopes
- **🔒 Immutability Control**: Per-configuration immutability and global release mode
- **🔄 Automatic Type Conversion**: Automatic string → int, float, bool, list, dict conversion
- **🔌 Plugin Architecture**: Extensible storage and plugin system
- **📊 Metadata Management**: Configuration statistics and state tracking

## 🚀 Quick Start

### Installation

```bash
pip install pyconfbox
```

### Basic Usage

```python
from pyconfbox import Config, ConfigScope

# Create Config instance
config = Config(default_storage="memory", fallback_storage="environment")

# Basic configuration
config.set("app_name", "MyApp")
config.set("debug", True)

# Type conversion
config.set("port", "8080", data_type=int)
config.set("timeout", "30.5", data_type=float)
config.set("hosts", "localhost,127.0.0.1", data_type=list)

# Scope-based configuration
config.set("database_url", "sqlite:///app.db", scope=ConfigScope.LOCAL)
config.set("secret_key", "super-secret", scope=ConfigScope.SECRET, immutable=True)

# Retrieve configuration
app_name = config.get("app_name")
port = config.get("port")  # Automatically int type
hosts = config.get("hosts")  # Automatically list type

# Scope-based retrieval
global_configs = config.get_by_scope(ConfigScope.GLOBAL)
secret_configs = config.get_by_scope(ConfigScope.SECRET)

# Release mode (lock all configurations)
config.release()
```

### File Storage Usage

```python
from pyconfbox import Config, JSONStorage, YAMLStorage, TOMLStorage

# JSON file storage
json_storage = JSONStorage('config.json')
config = Config(default_storage=json_storage)

config.set('app_name', 'MyApp')
config.set('version', '1.0.0')
config.set('features', ['auth', 'cache', 'logging'])

# YAML file storage
yaml_storage = YAMLStorage('config.yaml')
config = Config(default_storage=yaml_storage)

config.set('database', {
    'host': 'localhost',
    'port': 5432,
    'name': 'myapp_db'
})

# TOML file storage 
toml_storage = TOMLStorage('config.toml')
config = Config(default_storage=toml_storage)

config.set('owner', {
    'name': 'John Doe',
    'email': 'john@example.com'
})
```

### SQLite Storage Usage

```python
from pyconfbox import Config, SQLiteStorage

# In-memory SQLite
memory_storage = SQLiteStorage()  # ":memory:"
config = Config(default_storage=memory_storage)

# File SQLite
file_storage = SQLiteStorage('config.db')
config = Config(default_storage=file_storage)

config.set('session_timeout', 3600)
config.set('max_connections', 100)

# Batch update
batch_data = {
    'env': 'production',
    'region': 'us-west-2',
    'replicas': 3
}
file_storage.update(batch_data)
```

## 📋 Configuration Scopes

| Scope | Description | Use Cases |
|-------|-------------|-----------|
| `env` | Environment variables | OS environment variables, process-specific settings |
| `global` | Global variables | Application-wide settings |
| `local` | Local variables | Module/class-specific local settings |
| `system` | System variables | System-level settings |
| `secret` | Secret variables | Sensitive settings requiring encryption |
| `django` | Django settings | Django-specific settings |

## 🏗️ Storage Architecture

### Built-in Storage Backends
- **Memory**: In-memory storage (default)
- **Environment**: Environment variable storage (read-only)
- **File**: File-based storage (JSON, YAML, TOML)
- **Redis**: Redis storage
- **SQLite**: SQLite database storage

### Plugin Storage Backends (Separate Packages)
- **pyconfbox-mysql**: MySQL storage
- **pyconfbox-postgresql**: PostgreSQL storage
- **pyconfbox-mongodb**: MongoDB storage
- **pyconfbox-django**: Django integration plugin

## 🔒 Immutability Management

```python
# Set individual configuration as immutable
config.set("api_key", "secret", immutable=True)

# Attempt to change immutable configuration (raises exception)
try:
    config.set("api_key", "new_secret")
except ImmutableConfigError:
    print("Immutable configurations cannot be changed!")

# Lock all configurations (release mode)
config.release()

# Attempt to change configuration after release (raises exception)
try:
    config.set("new_key", "value")
except ReleasedConfigError:
    print("Released configurations cannot be changed!")
```

## 🔄 Automatic Type Conversion

```python
# String → Integer
config.set("port", "8080", data_type=int)
assert config.get("port") == 8080

# String → Boolean
config.set("debug", "true", data_type=bool)
assert config.get("debug") is True

# String → List (comma-separated)
config.set("hosts", "localhost,127.0.0.1", data_type=list)
assert config.get("hosts") == ["localhost", "127.0.0.1"]

# String → Dictionary (JSON)
config.set("db_config", '{"host": "localhost", "port": 5432}', data_type=dict)
assert config.get("db_config") == {"host": "localhost", "port": 5432}
```

## 📊 Metadata and Statistics

```python
metadata = config.get_metadata()

print(f"Total configurations: {metadata.total_configs}")
print(f"By scope: {metadata.scopes}")
print(f"By storage: {metadata.storages}")
print(f"Immutable count: {metadata.immutable_count}")
print(f"Is released: {metadata.is_released}")
```

## 🔌 Advanced Usage

### Environment Variable Prefix

```python
from pyconfbox import Config, EnvironmentStorage

# Use environment variables with prefix
env_storage = EnvironmentStorage(prefix="MYAPP_")
config = Config(default_storage=env_storage)

# Reads from MYAPP_DATABASE_URL environment variable
database_url = config.get("DATABASE_URL")
```

### Custom Storage Backend

```python
from pyconfbox.storage.base import BaseStorage
from pyconfbox.core.types import ConfigValue

class CustomStorage(BaseStorage):
    def get(self, key: str) -> ConfigValue | None:
        # Implementation
        pass
    
    def set(self, key: str, value: ConfigValue) -> None:
        # Implementation
        pass
    
    def delete(self, key: str) -> bool:
        # Implementation
        pass
    
    def list_keys(self) -> list[str]:
        # Implementation
        pass

# Use custom storage
custom_storage = CustomStorage()
config = Config(default_storage=custom_storage)
```

## 📖 Documentation

- **[Main Documentation](../../docs/README.md)** - Complete documentation
- **[API Reference](../../docs/en/api-reference.md)** - API documentation
- **[Examples](../../docs/en/examples.md)** - Usage examples
- **[한국어 문서](../../docs/ko/README.md)** - Korean documentation

## 🔗 Related Packages

- **[pyconfbox-django](../pyconfbox-django/)** - Django integration
- **[pyconfbox-mysql](../pyconfbox-mysql/)** - MySQL storage backend
- **[pyconfbox-postgresql](../pyconfbox-postgresql/)** - PostgreSQL storage backend
- **[pyconfbox-mongodb](../pyconfbox-mongodb/)** - MongoDB storage backend

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](../../.github/CONTRIBUTING.md) for details.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.

---

Experience better configuration management with **PyConfBox**! 🚀
