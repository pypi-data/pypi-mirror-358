"""PyConfBox SQLite 저장소."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.exceptions import StorageError
from .base import BaseStorage


class SQLiteStorage(BaseStorage):
    """SQLite 저장소 구현."""

    def __init__(
        self,
        db_path: str = ":memory:",
        table_name: str = "pyconfbox_config",
        **kwargs: Any
    ) -> None:
        """
        SQLite 저장소를 초기화합니다.

        Args:
            db_path: 데이터베이스 파일 경로 (":memory:"는 인메모리 DB)
            table_name: 테이블 이름
            **kwargs: 추가 설정
        """
        super().__init__(**kwargs)
        self.db_path = db_path
        self.table_name = table_name
        self._connection: Optional[sqlite3.Connection] = None

    def _do_initialize(self) -> None:
        """SQLite 데이터베이스를 초기화합니다."""
        try:
            # 파일 DB인 경우 디렉토리 생성
            if self.db_path != ":memory:":
                db_file = Path(self.db_path)
                db_file.parent.mkdir(parents=True, exist_ok=True)

            # 연결 생성
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # 멀티스레드 지원
                isolation_level=None      # autocommit 모드
            )

            # 테이블 생성
            self._create_table()

        except Exception as e:
            raise StorageError(f"Failed to initialize SQLite storage: {e}")

    def _create_table(self) -> None:
        """설정 테이블을 생성합니다."""
        if not self._connection:
            raise StorageError("SQLite connection not initialized")

        cursor = self._connection.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 업데이트 트리거 생성
        cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS update_{self.table_name}_timestamp
            AFTER UPDATE ON {self.table_name}
            FOR EACH ROW
            BEGIN
                UPDATE {self.table_name}
                SET updated_at = CURRENT_TIMESTAMP
                WHERE key = NEW.key;
            END
        """)

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
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(
                f"SELECT value FROM {self.table_name} WHERE key = ?",
                (key,)
            )

            result = cursor.fetchone()
            if result is None:
                return None

            return self._deserialize_value(result[0])

        except Exception as e:
            raise StorageError(f"Failed to get key '{key}' from SQLite: {e}")

    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장합니다.

        Args:
            key: 설정 키
            value: 설정 값
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            serialized_value = self._serialize_value(value)

            cursor.execute(f"""
                INSERT OR REPLACE INTO {self.table_name} (key, value)
                VALUES (?, ?)
            """, (key, serialized_value))

        except Exception as e:
            raise StorageError(f"Failed to set key '{key}' in SQLite: {e}")

    def delete(self, key: str) -> bool:
        """
        설정을 삭제합니다.

        Args:
            key: 설정 키

        Returns:
            삭제 성공 여부
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE key = ?",
                (key,)
            )

            return cursor.rowcount > 0

        except Exception as e:
            raise StorageError(f"Failed to delete key '{key}' from SQLite: {e}")

    def exists(self, key: str) -> bool:
        """
        설정 키가 존재하는지 확인합니다.

        Args:
            key: 설정 키

        Returns:
            존재 여부
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self.table_name} WHERE key = ? LIMIT 1",
                (key,)
            )

            return cursor.fetchone() is not None

        except Exception as e:
            raise StorageError(f"Failed to check existence of key '{key}' in SQLite: {e}")

    def keys(self) -> List[str]:
        """
        모든 설정 키를 반환합니다.

        Returns:
            설정 키 목록
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(f"SELECT key FROM {self.table_name}")

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            raise StorageError(f"Failed to get keys from SQLite: {e}")

    def clear(self) -> None:
        """모든 설정을 삭제합니다."""
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")

        except Exception as e:
            raise StorageError(f"Failed to clear SQLite storage: {e}")

    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 반환합니다.

        Returns:
            모든 설정의 딕셔너리
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(f"SELECT key, value FROM {self.table_name}")

            result = {}
            for row in cursor.fetchall():
                key, value = row
                result[key] = self._deserialize_value(value)

            return result

        except Exception as e:
            raise StorageError(f"Failed to get all data from SQLite: {e}")

    def update(self, data: Dict[str, Any]) -> None:
        """
        여러 설정을 한번에 업데이트합니다.

        Args:
            data: 업데이트할 설정 딕셔너리
        """
        if not self._connection:
            self.initialize()

        if not data:
            return

        try:
            cursor = self._connection.cursor()

            # 트랜잭션으로 배치 처리
            cursor.execute("BEGIN TRANSACTION")

            for key, value in data.items():
                serialized_value = self._serialize_value(value)
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {self.table_name} (key, value)
                    VALUES (?, ?)
                """, (key, serialized_value))

            cursor.execute("COMMIT")

        except Exception as e:
            if self._connection:
                cursor = self._connection.cursor()
                cursor.execute("ROLLBACK")
            raise StorageError(f"Failed to update SQLite storage: {e}")

    def close(self) -> None:
        """SQLite 연결을 종료합니다."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            finally:
                self._connection = None

    def get_metadata(self) -> Dict[str, Any]:
        """
        저장소 메타데이터를 반환합니다.

        Returns:
            메타데이터 딕셔너리
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()

            # 총 레코드 수
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total_count = cursor.fetchone()[0]

            # 가장 오래된/최신 레코드
            cursor.execute(f"""
                SELECT MIN(created_at), MAX(updated_at)
                FROM {self.table_name}
            """)
            dates = cursor.fetchone()

            return {
                "total_configs": total_count,
                "table_name": self.table_name,
                "db_path": self.db_path,
                "oldest_created": dates[0],
                "latest_updated": dates[1]
            }

        except Exception as e:
            raise StorageError(f"Failed to get SQLite metadata: {e}")

    def vacuum(self) -> None:
        """데이터베이스를 최적화합니다."""
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute("VACUUM")

        except Exception as e:
            raise StorageError(f"Failed to vacuum SQLite database: {e}")

    def get_table_info(self) -> List[Dict[str, Any]]:
        """
        테이블 정보를 반환합니다.

        Returns:
            테이블 컬럼 정보 목록
        """
        if not self._connection:
            self.initialize()

        try:
            cursor = self._connection.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")

            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default_value": row[4],
                    "pk": bool(row[5])
                })

            return columns

        except Exception as e:
            raise StorageError(f"Failed to get SQLite table info: {e}")

    def __repr__(self) -> str:
        """SQLite 저장소의 문자열 표현."""
        return (
            f"SQLiteStorage(db_path='{self.db_path}', "
            f"table_name='{self.table_name}', "
            f"initialized={self._initialized})"
        )
