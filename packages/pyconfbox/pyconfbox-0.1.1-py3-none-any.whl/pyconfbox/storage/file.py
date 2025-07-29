"""PyConfBox 파일 저장소."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.exceptions import StorageError
from .base import BaseStorage


class FileStorage(BaseStorage):
    """파일 기반 저장소 구현."""

    SUPPORTED_FORMATS = {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml"
    }

    def __init__(self, file_path: str, format: Optional[str] = None, **kwargs: Any) -> None:
        """
        파일 저장소를 초기화합니다.

        Args:
            file_path: 파일 경로
            format: 파일 형식 ("json", "yaml", "toml", None=자동감지)
            **kwargs: 추가 설정
        """
        super().__init__(**kwargs)
        self.file_path = Path(file_path)
        self.format = format or self._detect_format()
        self._data: Dict[str, Any] = {}
        self._loaded = False

    def _detect_format(self) -> str:
        """
        파일 확장자로부터 형식을 자동 감지합니다.

        Returns:
            파일 형식

        Raises:
            StorageError: 지원되지 않는 형식
        """
        suffix = self.file_path.suffix.lower()
        if suffix in self.SUPPORTED_FORMATS:
            return self.SUPPORTED_FORMATS[suffix]

        raise StorageError(f"Unsupported file format: {suffix}")

    def _do_initialize(self) -> None:
        """파일 저장소를 초기화합니다."""
        # 디렉토리가 없으면 생성
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일이 없으면 빈 파일 생성
        if not self.file_path.exists():
            self._save_data({})

        # 데이터 로드
        self._load_data()

    def _load_data(self) -> None:
        """파일에서 데이터를 로드합니다."""
        if not self.file_path.exists():
            self._data = {}
            return

        try:
            with open(self.file_path, encoding='utf-8') as f:
                content = f.read().strip()

                if not content:
                    self._data = {}
                    return

                if self.format == "json":
                    self._data = json.loads(content)
                elif self.format == "yaml":
                    import yaml
                    self._data = yaml.safe_load(content) or {}
                elif self.format == "toml":
                    import toml
                    self._data = toml.loads(content)
                else:
                    raise StorageError(f"Unsupported format: {self.format}")

        except Exception as e:
            raise StorageError(f"Failed to load file {self.file_path}: {e}")

        self._loaded = True

    def _save_data(self, data: Dict[str, Any]) -> None:
        """데이터를 파일에 저장합니다."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                if self.format == "json":
                    json.dump(data, f, indent=2, ensure_ascii=False)
                elif self.format == "yaml":
                    import yaml
                    yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
                elif self.format == "toml":
                    import toml
                    toml.dump(data, f)
                else:
                    raise StorageError(f"Unsupported format: {self.format}")

        except Exception as e:
            raise StorageError(f"Failed to save file {self.file_path}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """
        설정 값을 조회합니다.

        Args:
            key: 설정 키

        Returns:
            설정 값 (없으면 None)
        """
        if not self._loaded:
            self._load_data()

        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        if not self._loaded:
            self._load_data()

        self._data[key] = value
        self._save_data(self._data)

    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        if not self._loaded:
            self._load_data()

        if key in self._data:
            del self._data[key]
            self._save_data(self._data)
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
        if not self._loaded:
            self._load_data()

        return key in self._data

    def keys(self) -> List[str]:
        """
        모든 설정 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        if not self._loaded:
            self._load_data()

        return list(self._data.keys())

    def clear(self) -> None:
        """모든 설정을 삭제합니다."""
        self._data = {}
        self._save_data(self._data)

    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 반환합니다.

        Returns:
            모든 설정의 딕셔너리
        """
        if not self._loaded:
            self._load_data()

        return self._data.copy()

    def reload(self) -> None:
        """파일에서 데이터를 다시 로드합니다."""
        self._loaded = False
        self._load_data()

    def get_file_path(self) -> Path:
        """
        파일 경로를 반환합니다.

        Returns:
            파일 경로
        """
        return self.file_path

    def get_format(self) -> str:
        """
        파일 형식을 반환합니다.

        Returns:
            파일 형식
        """
        return self.format

    def __repr__(self) -> str:
        """파일 저장소의 문자열 표현."""
        return (
            f"FileStorage(path='{self.file_path}', "
            f"format='{self.format}', "
            f"initialized={self._initialized})"
        )


class JSONStorage(FileStorage):
    """JSON 파일 저장소."""

    def __init__(self, file_path: str, **kwargs: Any) -> None:
        """
        JSON 파일 저장소를 초기화합니다.

        Args:
            file_path: JSON 파일 경로
            **kwargs: 추가 설정
        """
        super().__init__(file_path, format="json", **kwargs)


class YAMLStorage(FileStorage):
    """YAML 파일 저장소."""

    def __init__(self, file_path: str, **kwargs: Any) -> None:
        """
        YAML 파일 저장소를 초기화합니다.

        Args:
            file_path: YAML 파일 경로
            **kwargs: 추가 설정
        """
        super().__init__(file_path, format="yaml", **kwargs)


class TOMLStorage(FileStorage):
    """TOML 파일 저장소."""

    def __init__(self, file_path: str, **kwargs: Any) -> None:
        """
        TOML 파일 저장소를 초기화합니다.

        Args:
            file_path: TOML 파일 경로
            **kwargs: 추가 설정
        """
        super().__init__(file_path, format="toml", **kwargs)
