"""PyConfBox 환경변수 저장소."""

import os
from typing import Any, Dict, List, Optional

from .base import ReadOnlyStorage


class EnvironmentStorage(ReadOnlyStorage):
    """환경변수 저장소 구현 (읽기 전용)."""

    def __init__(self, prefix: str = "", **kwargs: Any) -> None:
        """
        환경변수 저장소를 초기화합니다.

        Args:
            prefix: 환경변수 접두어 (예: "MYAPP_")
            **kwargs: 추가 설정
        """
        super().__init__(**kwargs)
        self.prefix = prefix

    def get(self, key: str) -> Optional[Any]:
        """
        환경변수 값을 조회합니다.

        Args:
            key: 설정 키

        Returns:
            환경변수 값 (없으면 None)
        """
        env_key = self._make_env_key(key)
        return os.environ.get(env_key)

    def exists(self, key: str) -> bool:
        """
        환경변수가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        env_key = self._make_env_key(key)
        return env_key in os.environ

    def keys(self) -> List[str]:
        """
        접두어와 일치하는 모든 환경변수 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        if not self.prefix:
            # 접두어가 없으면 모든 환경변수 반환
            return list(os.environ.keys())

        # 접두어가 있으면 해당 접두어로 시작하는 환경변수만 반환
        keys = []
        for env_key in os.environ.keys():
            if env_key.startswith(self.prefix):
                # 접두어를 제거한 키 반환
                key = env_key[len(self.prefix):]
                keys.append(key)
        return keys

    def get_all(self) -> Dict[str, Any]:
        """
        모든 환경변수를 반환합니다.

        Returns:
            모든 환경변수의 딕셔너리
        """
        result = {}
        for key in self.keys():
            result[key] = self.get(key)
        return result

    def _make_env_key(self, key: str) -> str:
        """
        설정 키를 환경변수 키로 변환합니다.

        Args:
            key: 설정 키

        Returns:
            환경변수 키
        """
        return f"{self.prefix}{key}"

    def get_prefix(self) -> str:
        """
        환경변수 접두어를 반환합니다.

        Returns:
            접두어
        """
        return self.prefix

    def set_prefix(self, prefix: str) -> None:
        """
        환경변수 접두어를 설정합니다.

        Args:
            prefix: 새로운 접두어
        """
        self.prefix = prefix

    def __repr__(self) -> str:
        """환경변수 저장소의 문자열 표현."""
        return f"EnvironmentStorage(prefix='{self.prefix}', initialized={self._initialized})"


class WritableEnvironmentStorage(EnvironmentStorage):
    """쓰기 가능한 환경변수 저장소."""

    def set(self, key: str, value: Any) -> None:
        """
        환경변수를 설정합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        env_key = self._make_env_key(key)
        os.environ[env_key] = str(value)

    def delete(self, key: str) -> bool:
        """
        환경변수를 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        env_key = self._make_env_key(key)
        if env_key in os.environ:
            del os.environ[env_key]
            return True
        return False

    def clear(self) -> None:
        """접두어와 일치하는 모든 환경변수를 삭제합니다."""
        keys_to_delete = []
        for env_key in os.environ.keys():
            if env_key.startswith(self.prefix):
                keys_to_delete.append(env_key)

        for env_key in keys_to_delete:
            del os.environ[env_key]

    def update(self, data: Dict[str, Any]) -> None:
        """
        여러 환경변수를 한번에 업데이트합니다.

        Args:
            data: 업데이트할 설정 딕셔너리
        """
        for key, value in data.items():
            self.set(key, str(value))

    def __repr__(self) -> str:
        """쓰기 가능한 환경변수 저장소의 문자열 표현."""
        return f"WritableEnvironmentStorage(prefix='{self.prefix}', initialized={self._initialized})"
