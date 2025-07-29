"""PyConfBox - Python configuration management with multiple storage backends."""

__version__ = "0.1.0"

from .core.config import Config
from .core.exceptions import (
    ConfigNotFoundError,
    ConfigTypeError,
    ImmutableConfigError,
    PluginError,
    PyConfBoxError,
    ReleasedConfigError,
    ScopeError,
    StorageError,
)
from .core.types import ConfigMetadata, ConfigScope, ConfigValue
from .storage.base import BaseStorage, ReadOnlyStorage
from .storage.environment import EnvironmentStorage, WritableEnvironmentStorage
from .storage.file import FileStorage, JSONStorage, TOMLStorage, YAMLStorage
from .storage.memory import MemoryStorage
from .storage.redis import RedisStorage
from .storage.sqlite import SQLiteStorage

# 선택적 import (Redis)
try:
    from .storage.redis import RedisStorage
except ImportError:
    RedisStorage = None

__all__ = [
    # 버전
    "__version__",

    # 메인 클래스
    "Config",

    # 예외
    "PyConfBoxError",
    "ConfigNotFoundError",
    "ImmutableConfigError",
    "ConfigTypeError",
    "StorageError",
    "PluginError",
    "ReleasedConfigError",
    "ScopeError",

    # 타입
    "ConfigScope",
    "ConfigValue",
    "ConfigMetadata",

    # 저장소
    "BaseStorage",
    "ReadOnlyStorage",
    "MemoryStorage",
    "EnvironmentStorage",
    "WritableEnvironmentStorage",
    "FileStorage",
    "JSONStorage",
    "YAMLStorage",
    "TOMLStorage",
    "RedisStorage",
    "SQLiteStorage",

    # Utility functions
    "check_optional_dependencies",
    "is_yaml_available",
    "is_toml_available",
    "is_redis_available",
    "is_crypto_available",
]


def check_optional_dependencies() -> dict:
    """
    선택적 의존성의 설치 상태를 확인합니다.

    Returns:
        각 의존성의 설치 상태를 담은 딕셔너리

    Example:
        >>> from pyconfbox import check_optional_dependencies
        >>> deps = check_optional_dependencies()
        >>> print(deps)
        {
            'yaml': True,
            'toml': False,
            'redis': True,
            'crypto': True
        }
    """
    dependencies = {}
    
    # YAML 지원 체크
    try:
        import yaml
        dependencies['yaml'] = True
    except ImportError:
        dependencies['yaml'] = False
    
    # TOML 지원 체크  
    try:
        import toml
        dependencies['toml'] = True
    except ImportError:
        dependencies['toml'] = False
    
    # Redis 지원 체크
    try:
        import redis
        dependencies['redis'] = True
    except ImportError:
        dependencies['redis'] = False
    
    # Cryptography 지원 체크
    try:
        import cryptography
        dependencies['crypto'] = True
    except ImportError:
        dependencies['crypto'] = False
    
    return dependencies


def is_yaml_available() -> bool:
    """YAML 지원이 가능한지 확인합니다."""
    try:
        import yaml
        return True
    except ImportError:
        return False


def is_toml_available() -> bool:
    """TOML 지원이 가능한지 확인합니다."""
    try:
        import toml
        return True
    except ImportError:
        return False


def is_redis_available() -> bool:
    """Redis 지원이 가능한지 확인합니다."""
    try:
        import redis
        return True
    except ImportError:
        return False


def is_crypto_available() -> bool:
    """암호화 지원이 가능한지 확인합니다."""
    try:
        import cryptography
        return True
    except ImportError:
        return False


