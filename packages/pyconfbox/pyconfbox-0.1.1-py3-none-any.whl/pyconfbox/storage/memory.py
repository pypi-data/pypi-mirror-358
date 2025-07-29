"""PyConfBox 메모리 저장소."""

from typing import Any, Dict, List, Optional

from .base import BaseStorage


class MemoryStorage(BaseStorage):
    """인메모리 저장소 구현."""

    def __init__(self, **kwargs: Any) -> None:
        """
        메모리 저장소를 초기화합니다.

        Args:
            **kwargs: 추가 설정 (현재 사용되지 않음)
        """
        super().__init__(**kwargs)
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        설정 값을 조회합니다.

        Args:
            key: 설정 키

        Returns:
            설정 값 (없으면 None)
        """
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        self._data[key] = value

    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        if key in self._data:
            del self._data[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """
        설정 키가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        return key in self._data

    def keys(self) -> List[str]:
        """
        모든 설정 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        return list(self._data.keys())

    def clear(self) -> None:
        """모든 설정을 삭제합니다."""
        self._data.clear()

    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 반환합니다.

        Returns:
            모든 설정의 딕셔너리
        """
        return self._data.copy()

    def size(self) -> int:
        """
        저장된 설정의 개수를 반환합니다.

        Returns:
            설정 개수
        """
        return len(self._data)

    def __len__(self) -> int:
        """저장된 설정의 개수를 반환합니다."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """설정 키가 존재하는지 확인합니다."""
        return key in self._data

    def __repr__(self) -> str:
        """메모리 저장소의 문자열 표현."""
        return f"MemoryStorage(size={len(self._data)}, initialized={self._initialized})"
