"""PyConfBox 메인 설정 관리 클래스."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from ..storage.base import BaseStorage
from ..storage.environment import EnvironmentStorage
from ..storage.memory import MemoryStorage
from .exceptions import (
    ConfigNotFoundError,
    ConfigTypeError,
    ReleasedConfigError,
    ScopeError,
    StorageError,
)
from .immutable import ImmutableManager
from .types import ConfigMetadata, ConfigScope, ConfigValue


class Config:
    """PyConfBox 메인 설정 관리 클래스."""

    def __init__(
        self,
        default_storage: Union[str, BaseStorage] = "memory",
        fallback_storage: Optional[Union[str, BaseStorage]] = None,
        **storage_configs: Any
    ) -> None:
        """
        설정 관리자를 초기화합니다.

        Args:
            default_storage: 기본 저장소 (타입 문자열 또는 저장소 객체)
            fallback_storage: 폴백 저장소 (타입 문자열 또는 저장소 객체)
            **storage_configs: 저장소별 설정
        """
        self._configs: Dict[str, ConfigValue] = {}
        self._metadata = ConfigMetadata()
        self._immutable_manager = ImmutableManager()

        # 저장소 설정
        self._storage_configs = storage_configs
        self._storages: Dict[str, BaseStorage] = {}

        # 기본 저장소들 초기화
        self._init_default_storages()

        # 기본 저장소 설정
        if isinstance(default_storage, BaseStorage):
            storage_name = f"custom_{id(default_storage)}"
            self._storages[storage_name] = default_storage
            self._default_storage = storage_name
        else:
            self._default_storage = default_storage

        # 폴백 저장소 설정
        if isinstance(fallback_storage, BaseStorage):
            storage_name = f"custom_{id(fallback_storage)}"
            self._storages[storage_name] = fallback_storage
            self._fallback_storage = storage_name
        else:
            self._fallback_storage = fallback_storage

    def _init_default_storages(self) -> None:
        """기본 저장소들을 초기화합니다."""
        # 메모리 저장소
        self._storages["memory"] = MemoryStorage()

        # 환경변수 저장소
        env_prefix = self._storage_configs.get("env_prefix", "")
        self._storages["environment"] = EnvironmentStorage(prefix=env_prefix)
        self._storages["env"] = self._storages["environment"]  # 별칭

    def set(
        self,
        key: str,
        value: Any,
        scope: Union[str, ConfigScope] = ConfigScope.GLOBAL,
        data_type: Optional[Type] = None,
        immutable: bool = False,
        storage: Optional[str] = None,
    ) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
            scope: 설정 범위
            data_type: 데이터 타입
            immutable: 불변 여부
            storage: 저장소 타입

        Raises:
            ReleasedConfigError: 설정이 릴리즈된 경우
            ImmutableConfigError: 설정이 불변인 경우
            ConfigTypeError: 타입이 올바르지 않은 경우
            ScopeError: 잘못된 범위인 경우
        """
        # 범위 검증
        if isinstance(scope, str):
            try:
                scope = ConfigScope(scope)
            except ValueError:
                raise ScopeError(scope)

        # 설정 값 객체 생성
        config_value = ConfigValue(
            key=key,
            value=value,
            scope=scope,
            data_type=data_type,
            immutable=immutable,
            storage=storage or self._default_storage,
            created_at=datetime.now().isoformat(),
        )

        # 타입 검증 및 변환
        if data_type is not None:
            if not config_value.validate_type():
                raise ConfigTypeError(key, data_type, type(value))
            config_value.value = config_value.convert_type()

        # 기존 설정이 있는 경우 불변성 검사
        if key in self._configs:
            self._immutable_manager.check_mutable(key)
            config_value.created_at = self._configs[key].created_at
            config_value.updated_at = datetime.now().isoformat()
            # 메타데이터에서 기존 설정 제거
            self._metadata.remove_config(self._configs[key])
        else:
            # 새로운 설정의 불변성 검사
            self._immutable_manager.validate_config_change(config_value)

        # 설정 저장
        self._configs[key] = config_value
        self._metadata.add_config(config_value)

        # 저장소에 저장
        self._save_to_storage(config_value)

    def get(
        self,
        key: str,
        default: Any = None,
        scope: Optional[Union[str, ConfigScope]] = None,
        data_type: Optional[Type] = None,
    ) -> Any:
        """
        설정 값을 조회합니다.

        Args:
            key: 설정 키
            default: 기본값
            scope: 범위 필터
            data_type: 데이터 타입

        Returns:
            설정 값

        Raises:
            ConfigNotFoundError: 설정을 찾을 수 없는 경우 (default가 None인 경우)
            ConfigTypeError: 타입 변환에 실패한 경우
        """
        # 메모리에서 먼저 검색
        if key in self._configs:
            config_value = self._configs[key]

            # 범위 필터 확인
            if scope is not None:
                if isinstance(scope, str):
                    scope = ConfigScope(scope)
                if config_value.scope != scope:
                    if default is None:
                        raise ConfigNotFoundError(key)
                    return default

            value = config_value.value

            # 타입 변환
            if data_type is not None and not isinstance(value, data_type):
                try:
                    if data_type is bool and isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes')
                    else:
                        value = data_type(value)
                except (ValueError, TypeError) as e:
                    raise ConfigTypeError(key, data_type, type(value)) from e

            return value

        # 저장소에서 검색
        value = self._load_from_storage(key)
        if value is not None:
            # 타입 변환
            if data_type is not None:
                try:
                    if data_type is bool and isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes')
                    else:
                        value = data_type(value)
                except (ValueError, TypeError) as e:
                    raise ConfigTypeError(key, data_type, type(value)) from e
            return value

        # 기본값 반환
        if default is None:
            raise ConfigNotFoundError(key)
        return default

    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부

        Raises:
            ReleasedConfigError: 설정이 릴리즈된 경우
            ImmutableConfigError: 설정이 불변인 경우
        """
        self._immutable_manager.check_mutable(key)

        deleted = False

        # 메모리에서 삭제
        if key in self._configs:
            config_value = self._configs[key]
            del self._configs[key]
            self._metadata.remove_config(config_value)
            self._immutable_manager.unmark_immutable(key)
            deleted = True

        # 저장소에서 삭제 (읽기 전용 저장소는 건너뛰기)
        for storage in self._storages.values():
            try:
                if hasattr(storage, 'delete') and storage.delete(key):
                    deleted = True
            except NotImplementedError:
                # 읽기 전용 저장소는 무시
                pass

        return deleted

    def exists(self, key: str) -> bool:
        """
        설정 키가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        # 메모리에서 확인
        if key in self._configs:
            return True

        # 저장소에서 확인
        return self._load_from_storage(key) is not None

    def keys(self, scope: Optional[Union[str, ConfigScope]] = None) -> List[str]:
        """
        설정 키 목록을 반환합니다.

        Args:
            scope: 범위 필터

        Returns:
            설정 키 목록
        """
        if isinstance(scope, str):
            scope = ConfigScope(scope)

        keys = set()

        # 메모리에서 키 수집 (범위 필터링 적용)
        for key, config_value in self._configs.items():
            if scope is None or config_value.scope == scope:
                keys.add(key)

        # 범위 필터가 없는 경우에만 저장소에서 키 수집
        if scope is None:
            for storage in self._storages.values():
                try:
                    storage_keys = storage.keys()
                    keys.update(storage_keys)
                except Exception:
                    # 저장소에서 키를 가져올 수 없는 경우 무시
                    pass

        return list(keys)

    def get_by_scope(self, scope: Union[str, ConfigScope]) -> Dict[str, Any]:
        """
        특정 범위의 모든 설정을 반환합니다.

        Args:
            scope: 설정 범위

        Returns:
            범위별 설정 딕셔너리
        """
        if isinstance(scope, str):
            scope = ConfigScope(scope)

        result = {}
        for key, config_value in self._configs.items():
            if config_value.scope == scope:
                result[key] = config_value.value

        return result

    def update(self, data: Dict[str, Any], **kwargs: Any) -> None:
        """
        여러 설정을 한번에 업데이트합니다.

        Args:
            data: 업데이트할 설정 딕셔너리
            **kwargs: set 메서드에 전달할 추가 인수
        """
        for key, value in data.items():
            self.set(key, value, **kwargs)

    def clear(self, scope: Optional[Union[str, ConfigScope]] = None) -> None:
        """
        설정을 삭제합니다.

        Args:
            scope: 범위 필터 (None이면 모든 설정 삭제)

        Raises:
            ReleasedConfigError: 설정이 릴리즈된 경우
        """
        if self._immutable_manager.is_released():
            raise ReleasedConfigError()

        keys_to_delete = []
        for key, config_value in self._configs.items():
            if scope is None or config_value.scope == scope:
                if not self._immutable_manager.is_immutable(key):
                    keys_to_delete.append(key)

        for key in keys_to_delete:
            self.delete(key)

    def release(self) -> None:
        """
        모든 설정을 불변으로 고정합니다.

        릴리즈 후에는 어떤 설정도 변경할 수 없습니다.
        """
        self._immutable_manager.release()
        self._metadata.is_released = True

    def is_released(self) -> bool:
        """
        설정이 릴리즈되었는지 확인합니다.

        Returns:
            릴리즈 여부
        """
        return self._immutable_manager.is_released()

    def get_metadata(self) -> ConfigMetadata:
        """
        설정 메타데이터를 반환합니다.

        Returns:
            설정 메타데이터
        """
        return self._metadata

    def _save_to_storage(self, config_value: ConfigValue) -> None:
        """설정을 저장소에 저장합니다."""
        storage_name = config_value.storage or self._default_storage

        if storage_name in self._storages:
            storage = self._storages[storage_name]
            try:
                storage.set(config_value.key, config_value.value)
            except Exception as e:
                raise StorageError(f"Failed to save to {storage_name}: {e}", storage_name)

    def _load_from_storage(self, key: str) -> Optional[Any]:
        """저장소에서 설정을 로드합니다."""
        # 기본 저장소에서 먼저 시도
        if self._default_storage in self._storages:
            storage = self._storages[self._default_storage]
            try:
                value = storage.get(key)
                if value is not None:
                    return value
            except Exception:
                pass

        # 폴백 저장소에서 시도
        if self._fallback_storage and self._fallback_storage in self._storages:
            storage = self._storages[self._fallback_storage]
            try:
                value = storage.get(key)
                if value is not None:
                    return value
            except Exception:
                pass

        return None

    def __repr__(self) -> str:
        """Config의 문자열 표현."""
        return (
            f"Config(configs={len(self._configs)}, "
            f"released={self._immutable_manager.is_released()}, "
            f"default_storage='{self._default_storage}')"
        )
