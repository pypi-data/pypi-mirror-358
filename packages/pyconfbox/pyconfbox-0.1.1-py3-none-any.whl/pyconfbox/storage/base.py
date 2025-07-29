"""PyConfBox 저장소 기본 인터페이스."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseStorage(ABC):
    """저장소의 기본 추상 클래스."""

    def __init__(self, **kwargs: Any) -> None:
        """
        저장소를 초기화합니다.

        Args:
            **kwargs: 저장소별 설정 옵션
        """
        self._initialized = False
        self._config = kwargs

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        설정 값을 조회합니다.

        Args:
            key: 설정 키

        Returns:
            설정 값 (없으면 None)
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        설정 키가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        pass

    @abstractmethod
    def keys(self) -> List[str]:
        """
        모든 설정 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 설정을 삭제합니다."""
        pass

    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 반환합니다.

        Returns:
            모든 설정의 딕셔너리
        """
        result = {}
        for key in self.keys():
            result[key] = self.get(key)
        return result

    def update(self, data: Dict[str, Any]) -> None:
        """
        여러 설정을 한번에 업데이트합니다.

        Args:
            data: 업데이트할 설정 딕셔너리
        """
        for key, value in data.items():
            self.set(key, value)

    def initialize(self) -> None:
        """
        저장소를 초기화합니다.

        이 메서드는 저장소가 처음 사용될 때 호출됩니다.
        """
        if not self._initialized:
            self._do_initialize()
            self._initialized = True

    def _do_initialize(self) -> None:
        """
        실제 초기화 작업을 수행합니다.

        서브클래스에서 필요시 오버라이드합니다.
        """
        pass

    def is_initialized(self) -> bool:
        """
        저장소가 초기화되었는지 확인합니다.

        Returns:
            초기화 여부
        """
        return self._initialized

    def get_config(self) -> Dict[str, Any]:
        """
        저장소 설정을 반환합니다.

        Returns:
            저장소 설정 딕셔너리
        """
        return self._config.copy()

    def close(self) -> None:
        """
        저장소 연결을 종료합니다.

        서브클래스에서 필요시 오버라이드합니다.
        """
        pass

    def __enter__(self) -> "BaseStorage":
        """컨텍스트 매니저 진입."""
        self.initialize()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """컨텍스트 매니저 종료."""
        self.close()

    def __repr__(self) -> str:
        """저장소의 문자열 표현."""
        return f"{self.__class__.__name__}(initialized={self._initialized})"


class ReadOnlyStorage(BaseStorage):
    """읽기 전용 저장소 기본 클래스."""

    def set(self, key: str, value: Any) -> None:
        """
        읽기 전용 저장소에서는 설정할 수 없습니다.

        Args:
            key: 설정 키
            value: 설정 값

        Raises:
            NotImplementedError: 항상 발생
        """
        raise NotImplementedError("This storage is read-only")

    def delete(self, key: str) -> bool:
        """
        읽기 전용 저장소에서는 삭제할 수 없습니다.

        Args:
            key: 설정 키

        Returns:
            항상 False

        Raises:
            NotImplementedError: 항상 발생
        """
        raise NotImplementedError("This storage is read-only")

    def clear(self) -> None:
        """
        읽기 전용 저장소에서는 삭제할 수 없습니다.

        Raises:
            NotImplementedError: 항상 발생
        """
        raise NotImplementedError("This storage is read-only")

    def update(self, data: Dict[str, Any]) -> None:
        """
        읽기 전용 저장소에서는 업데이트할 수 없습니다.

        Args:
            data: 업데이트할 설정 딕셔너리

        Raises:
            NotImplementedError: 항상 발생
        """
        raise NotImplementedError("This storage is read-only")
