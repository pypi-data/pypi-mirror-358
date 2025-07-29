"""PyConfBox 커스텀 예외 클래스들."""

from typing import Optional


class PyConfBoxError(Exception):
    """PyConfBox 기본 예외 클래스."""

    def __init__(self, message: str, key: Optional[str] = None) -> None:
        """
        PyConfBox 기본 예외를 초기화합니다.

        Args:
            message: 오류 메시지
            key: 관련된 설정 키 (선택적)
        """
        super().__init__(message)
        self.key = key


class ConfigNotFoundError(PyConfBoxError):
    """설정 키를 찾을 수 없을 때 발생하는 예외."""

    def __init__(self, key: str) -> None:
        """
        설정 키를 찾을 수 없을 때 발생하는 예외를 초기화합니다.

        Args:
            key: 찾을 수 없는 설정 키
        """
        super().__init__(f"Configuration key '{key}' not found", key)


class ImmutableConfigError(PyConfBoxError):
    """불변 설정을 변경하려고 할 때 발생하는 예외."""

    def __init__(self, key: str) -> None:
        """
        불변 설정 변경 시도 시 발생하는 예외를 초기화합니다.

        Args:
            key: 변경하려는 불변 설정 키
        """
        super().__init__(f"Configuration key '{key}' is immutable and cannot be changed", key)


class ConfigTypeError(PyConfBoxError):
    """설정 값의 타입이 올바르지 않을 때 발생하는 예외."""

    def __init__(self, key: str, expected_type: type, actual_type: type) -> None:
        """
        설정 값의 타입 오류 시 발생하는 예외를 초기화합니다.

        Args:
            key: 설정 키
            expected_type: 예상 타입
            actual_type: 실제 타입
        """
        message = (
            f"Configuration key '{key}' expects type {expected_type.__name__}, "
            f"but got {actual_type.__name__}"
        )
        super().__init__(message, key)
        self.expected_type = expected_type
        self.actual_type = actual_type


class StorageError(PyConfBoxError):
    """저장소 관련 오류가 발생할 때 발생하는 예외."""

    def __init__(self, message: str, storage_type: Optional[str] = None) -> None:
        """
        저장소 오류 시 발생하는 예외를 초기화합니다.

        Args:
            message: 오류 메시지
            storage_type: 저장소 타입 (선택적)
        """
        super().__init__(message)
        self.storage_type = storage_type


class PluginError(PyConfBoxError):
    """플러그인 관련 오류가 발생할 때 발생하는 예외."""

    def __init__(self, message: str, plugin_name: Optional[str] = None) -> None:
        """
        플러그인 오류 시 발생하는 예외를 초기화합니다.

        Args:
            message: 오류 메시지
            plugin_name: 플러그인 이름 (선택적)
        """
        super().__init__(message)
        self.plugin_name = plugin_name


class ReleasedConfigError(PyConfBoxError):
    """릴리즈된 설정을 변경하려고 할 때 발생하는 예외."""

    def __init__(self) -> None:
        """릴리즈된 설정 변경 시도 시 발생하는 예외를 초기화합니다."""
        super().__init__("Configuration is released and cannot be modified")


class ScopeError(PyConfBoxError):
    """잘못된 범위(scope)를 사용할 때 발생하는 예외."""

    def __init__(self, scope: str) -> None:
        """
        잘못된 범위 사용 시 발생하는 예외를 초기화합니다.

        Args:
            scope: 잘못된 범위 이름
        """
        super().__init__(f"Invalid scope '{scope}'")
        self.scope = scope
