"""PyConfBox Redis 저장소."""

import json
from typing import Any, Dict, List, Optional

from ..core.exceptions import StorageError
from .base import BaseStorage


class RedisStorage(BaseStorage):
    """Redis 저장소 구현."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "pyconfbox:",
        decode_responses: bool = True,
        **redis_kwargs: Any
    ) -> None:
        """
        Redis 저장소를 초기화합니다.

        Args:
            host: Redis 호스트
            port: Redis 포트
            db: Redis 데이터베이스 번호
            password: Redis 비밀번호
            prefix: 키 접두어
            decode_responses: 응답 디코딩 여부
            **redis_kwargs: Redis 클라이언트 추가 설정
        """
        super().__init__()
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.decode_responses = decode_responses
        self.redis_kwargs = redis_kwargs
        self._client: Optional[Any] = None

    def _do_initialize(self) -> None:
        """Redis 클라이언트를 초기화합니다."""
        try:
            import redis

            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                **self.redis_kwargs
            )

            # 연결 테스트
            self._client.ping()

        except ImportError:
            raise StorageError(
                "Redis package not found. Install with: pip install redis"
            )
        except Exception as e:
            raise StorageError(f"Failed to connect to Redis: {e}")

    def _make_key(self, key: str) -> str:
        """
        설정 키를 Redis 키로 변환합니다.

        Args:
            key: 설정 키

        Returns:
            Redis 키
        """
        return f"{self.prefix}{key}"

    def _serialize_value(self, value: Any) -> str:
        """
        값을 직렬화합니다.

        Args:
            value: 직렬화할 값

        Returns:
            직렬화된 문자열
        """
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _deserialize_value(self, value: str) -> Any:
        """
        값을 역직렬화합니다.

        Args:
            value: 역직렬화할 문자열

        Returns:
            역직렬화된 값
        """
        if not value:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # JSON이 아닌 경우 문자열로 반환
            return value

    def get(self, key: str) -> Optional[Any]:
        """
        설정 값을 조회합니다.

        Args:
            key: 설정 키

        Returns:
            설정 값 (없으면 None)
        """
        if not self._client:
            self.initialize()

        try:
            redis_key = self._make_key(key)
            value = self._client.get(redis_key)

            if value is None:
                return None

            return self._deserialize_value(value)

        except Exception as e:
            raise StorageError(f"Failed to get key '{key}' from Redis: {e}")

    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        if not self._client:
            self.initialize()

        try:
            redis_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            self._client.set(redis_key, serialized_value)

        except Exception as e:
            raise StorageError(f"Failed to set key '{key}' in Redis: {e}")

    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        if not self._client:
            self.initialize()

        try:
            redis_key = self._make_key(key)
            result = self._client.delete(redis_key)
            return result > 0

        except Exception as e:
            raise StorageError(f"Failed to delete key '{key}' from Redis: {e}")

    def exists(self, key: str) -> bool:
        """
        설정 키가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        if not self._client:
            self.initialize()

        try:
            redis_key = self._make_key(key)
            return bool(self._client.exists(redis_key))

        except Exception as e:
            raise StorageError(f"Failed to check existence of key '{key}' in Redis: {e}")

    def keys(self) -> List[str]:
        """
        모든 설정 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        if not self._client:
            self.initialize()

        try:
            pattern = f"{self.prefix}*"
            redis_keys = self._client.keys(pattern)

            # 접두어 제거
            prefix_len = len(self.prefix)
            return [key[prefix_len:] for key in redis_keys]

        except Exception as e:
            raise StorageError(f"Failed to get keys from Redis: {e}")

    def clear(self) -> None:
        """모든 설정을 삭제합니다."""
        if not self._client:
            self.initialize()

        try:
            pattern = f"{self.prefix}*"
            redis_keys = self._client.keys(pattern)

            if redis_keys:
                self._client.delete(*redis_keys)

        except Exception as e:
            raise StorageError(f"Failed to clear Redis storage: {e}")

    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 반환합니다.

        Returns:
            모든 설정의 딕셔너리
        """
        if not self._client:
            self.initialize()

        try:
            pattern = f"{self.prefix}*"
            redis_keys = self._client.keys(pattern)

            if not redis_keys:
                return {}

            # 모든 값을 한 번에 가져오기
            values = self._client.mget(redis_keys)

            result = {}
            prefix_len = len(self.prefix)

            for redis_key, value in zip(redis_keys, values):
                key = redis_key[prefix_len:]
                result[key] = self._deserialize_value(value)

            return result

        except Exception as e:
            raise StorageError(f"Failed to get all data from Redis: {e}")

    def update(self, data: Dict[str, Any]) -> None:
        """
        여러 설정을 한번에 업데이트합니다.

        Args:
            data: 업데이트할 설정 딕셔너리
        """
        if not self._client:
            self.initialize()

        if not data:
            return

        try:
            # 파이프라인을 사용하여 배치 처리
            pipe = self._client.pipeline()

            for key, value in data.items():
                redis_key = self._make_key(key)
                serialized_value = self._serialize_value(value)
                pipe.set(redis_key, serialized_value)

            pipe.execute()

        except Exception as e:
            raise StorageError(f"Failed to update Redis storage: {e}")

    def close(self) -> None:
        """Redis 연결을 종료합니다."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            finally:
                self._client = None

    def ping(self) -> bool:
        """
        Redis 연결 상태를 확인합니다.

        Returns:
            연결 상태
        """
        if not self._client:
            return False

        try:
            return self._client.ping()
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Redis 서버 정보를 반환합니다.

        Returns:
            서버 정보 딕셔너리
        """
        if not self._client:
            self.initialize()

        try:
            return self._client.info()
        except Exception as e:
            raise StorageError(f"Failed to get Redis info: {e}")

    def __repr__(self) -> str:
        """Redis 저장소의 문자열 표현."""
        return (
            f"RedisStorage(host='{self.host}', port={self.port}, "
            f"db={self.db}, prefix='{self.prefix}', "
            f"initialized={self._initialized})"
        )
