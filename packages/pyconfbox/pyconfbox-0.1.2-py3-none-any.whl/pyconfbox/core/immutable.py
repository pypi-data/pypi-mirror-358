"""PyConfBox 불변성 관리 시스템."""

from datetime import datetime
from typing import Dict, Optional, Set

from .exceptions import ImmutableConfigError, ReleasedConfigError
from .types import ConfigValue


class ImmutableManager:
    """설정의 불변성을 관리하는 클래스."""

    def __init__(self) -> None:
        """불변성 관리자를 초기화합니다."""
        self._immutable_keys: Set[str] = set()
        self._released: bool = False
        self._release_time: Optional[datetime] = None

    def mark_immutable(self, key: str) -> None:
        """
        설정 키를 불변으로 표시합니다.

        Args:
            key: 불변으로 표시할 설정 키
        """
        self._immutable_keys.add(key)

    def unmark_immutable(self, key: str) -> None:
        """
        설정 키의 불변 표시를 해제합니다.

        Args:
            key: 불변 표시를 해제할 설정 키
        """
        self._immutable_keys.discard(key)

    def is_immutable(self, key: str) -> bool:
        """
        설정 키가 불변인지 확인합니다.

        Args:
            key: 확인할 설정 키

        Returns:
            불변 여부
        """
        return key in self._immutable_keys

    def check_mutable(self, key: str) -> None:
        """
        설정 키가 변경 가능한지 확인합니다.

        Args:
            key: 확인할 설정 키

        Raises:
            ReleasedConfigError: 설정이 릴리즈된 경우
            ImmutableConfigError: 설정이 불변인 경우
        """
        if self._released:
            raise ReleasedConfigError()

        if self.is_immutable(key):
            raise ImmutableConfigError(key)

    def release(self) -> None:
        """
        모든 설정을 불변으로 고정합니다 (릴리즈 모드).

        릴리즈 후에는 어떤 설정도 변경할 수 없습니다.
        """
        self._released = True
        self._release_time = datetime.now()

    def is_released(self) -> bool:
        """
        설정이 릴리즈되었는지 확인합니다.

        Returns:
            릴리즈 여부
        """
        return self._released

    def get_release_time(self) -> Optional[datetime]:
        """
        릴리즈 시간을 반환합니다.

        Returns:
            릴리즈 시간 (릴리즈되지 않은 경우 None)
        """
        return self._release_time

    def get_immutable_keys(self) -> Set[str]:
        """
        불변 설정 키 목록을 반환합니다.

        Returns:
            불변 설정 키 집합
        """
        return self._immutable_keys.copy()

    def get_status(self) -> Dict[str, any]:
        """
        불변성 관리자의 상태를 반환합니다.

        Returns:
            상태 정보 딕셔너리
        """
        return {
            "released": self._released,
            "release_time": self._release_time.isoformat() if self._release_time else None,
            "immutable_keys_count": len(self._immutable_keys),
            "immutable_keys": list(self._immutable_keys)
        }

    def reset(self) -> None:
        """
        불변성 관리자를 초기 상태로 리셋합니다.

        주의: 이 메서드는 테스트 목적으로만 사용해야 합니다.
        """
        self._immutable_keys.clear()
        self._released = False
        self._release_time = None

    def validate_config_change(self, config_value: ConfigValue) -> None:
        """
        설정 변경이 가능한지 검증합니다.

        Args:
            config_value: 변경하려는 설정 값

        Raises:
            ReleasedConfigError: 설정이 릴리즈된 경우
            ImmutableConfigError: 설정이 불변인 경우
        """
        self.check_mutable(config_value.key)

        # 새로운 설정이 불변으로 설정되는 경우 즉시 불변 목록에 추가
        if config_value.immutable:
            self.mark_immutable(config_value.key)
