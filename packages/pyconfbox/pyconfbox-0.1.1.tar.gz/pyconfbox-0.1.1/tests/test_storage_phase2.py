"""PyConfBox Phase 2 저장소 테스트."""

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pyconfbox import (
    Config,
    FileStorage,
    JSONStorage,
    RedisStorage,
    SQLiteStorage,
    StorageError,
    TOMLStorage,
    YAMLStorage,
)

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


class TestFileStorage:
    """파일 저장소 테스트."""

    def test_json_storage_basic(self) -> None:
        """JSON 저장소 기본 동작 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            storage = JSONStorage(str(file_path))
            storage.initialize()

            # 설정 저장
            storage.set("test_key", "test_value")
            assert storage.get("test_key") == "test_value"

            # 파일 확인
            assert file_path.exists()
            with open(file_path) as f:
                data = json.load(f)
                assert data["test_key"] == "test_value"

    def test_json_storage_types(self) -> None:
        """JSON 저장소 타입 변환 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            storage = JSONStorage(str(file_path))
            storage.initialize()

            # 다양한 타입 저장
            test_data = {
                "string": "hello",
                "number": 42,
                "float": 3.14,
                "boolean": True,
                "list": [1, 2, 3],
                "dict": {"nested": "value"}
            }

            for key, value in test_data.items():
                storage.set(key, value)
                assert storage.get(key) == value

    def test_yaml_storage_basic(self) -> None:
        """YAML 저장소 기본 동작 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.yaml"
            storage = YAMLStorage(str(file_path))
            storage.initialize()

            # 설정 저장
            storage.set("test_key", "test_value")
            assert storage.get("test_key") == "test_value"

            # 파일 확인
            assert file_path.exists()

    def test_toml_storage_basic(self) -> None:
        """TOML 저장소 기본 동작 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.toml"
            storage = TOMLStorage(str(file_path))
            storage.initialize()

            # 설정 저장
            storage.set("test_key", "test_value")
            assert storage.get("test_key") == "test_value"

            # 파일 확인
            assert file_path.exists()

    def test_file_storage_auto_detect(self) -> None:
        """파일 확장자 자동 감지 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # JSON 파일
            json_path = Path(temp_dir) / "config.json"
            json_storage = FileStorage(str(json_path))
            assert json_storage.get_format() == "json"

            # YAML 파일
            yaml_path = Path(temp_dir) / "config.yaml"
            yaml_storage = FileStorage(str(yaml_path))
            assert yaml_storage.get_format() == "yaml"

            # TOML 파일
            toml_path = Path(temp_dir) / "config.toml"
            toml_storage = FileStorage(str(toml_path))
            assert toml_storage.get_format() == "toml"

    def test_file_storage_unsupported_format(self) -> None:
        """지원되지 않는 파일 형식 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.txt"

            with pytest.raises(StorageError, match="Unsupported file format"):
                FileStorage(str(file_path))

    def test_file_storage_crud_operations(self) -> None:
        """파일 저장소 CRUD 동작 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            storage = JSONStorage(str(file_path))
            storage.initialize()

            # Create
            storage.set("key1", "value1")
            storage.set("key2", "value2")

            # Read
            assert storage.get("key1") == "value1"
            assert storage.get("key2") == "value2"
            assert storage.get("nonexistent") is None

            # Update
            storage.set("key1", "updated_value")
            assert storage.get("key1") == "updated_value"

            # Delete
            assert storage.delete("key1") is True
            assert storage.get("key1") is None
            assert storage.delete("nonexistent") is False

            # Keys
            assert "key2" in storage.keys()
            assert "key1" not in storage.keys()

            # Exists
            assert storage.exists("key2") is True
            assert storage.exists("key1") is False

            # Clear
            storage.clear()
            assert len(storage.keys()) == 0

    def test_file_storage_reload(self) -> None:
        """파일 저장소 리로드 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            storage = JSONStorage(str(file_path))
            storage.initialize()

            # 데이터 저장
            storage.set("key1", "value1")

            # 파일 직접 수정
            with open(file_path, 'w') as f:
                json.dump({"key1": "modified", "key2": "new"}, f)

            # 리로드 전에는 이전 값
            assert storage.get("key1") == "value1"
            assert storage.get("key2") is None

            # 리로드 후에는 새 값
            storage.reload()
            assert storage.get("key1") == "modified"
            assert storage.get("key2") == "new"


class TestSQLiteStorage:
    """SQLite 저장소 테스트."""

    def test_sqlite_memory_storage(self) -> None:
        """SQLite 인메모리 저장소 테스트."""
        storage = SQLiteStorage()  # 기본값은 ":memory:"
        storage.initialize()

        # 기본 동작
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        # 메타데이터
        metadata = storage.get_metadata()
        assert metadata["total_configs"] == 1
        assert metadata["db_path"] == ":memory:"

    def test_sqlite_file_storage(self) -> None:
        """SQLite 파일 저장소 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "config.db"
            storage = SQLiteStorage(str(db_path))
            storage.initialize()

            # 설정 저장
            storage.set("test_key", "test_value")
            assert storage.get("test_key") == "test_value"

            # 파일 확인
            assert db_path.exists()

    def test_sqlite_crud_operations(self) -> None:
        """SQLite 저장소 CRUD 동작 테스트."""
        storage = SQLiteStorage()
        storage.initialize()

        # Create
        storage.set("key1", "value1")
        storage.set("key2", {"nested": "value"})

        # Read
        assert storage.get("key1") == "value1"
        assert storage.get("key2") == {"nested": "value"}
        assert storage.get("nonexistent") is None

        # Update
        storage.set("key1", "updated_value")
        assert storage.get("key1") == "updated_value"

        # Delete
        assert storage.delete("key1") is True
        assert storage.get("key1") is None
        assert storage.delete("nonexistent") is False

        # Keys
        assert "key2" in storage.keys()
        assert "key1" not in storage.keys()

        # Exists
        assert storage.exists("key2") is True
        assert storage.exists("key1") is False

        # Clear
        storage.clear()
        assert len(storage.keys()) == 0

    def test_sqlite_batch_update(self) -> None:
        """SQLite 배치 업데이트 테스트."""
        storage = SQLiteStorage()
        storage.initialize()

        # 배치 업데이트
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": {"nested": "value"}
        }
        storage.update(data)

        # 확인
        for key, expected_value in data.items():
            assert storage.get(key) == expected_value

    def test_sqlite_table_info(self) -> None:
        """SQLite 테이블 정보 테스트."""
        storage = SQLiteStorage()
        storage.initialize()

        table_info = storage.get_table_info()
        assert len(table_info) == 4  # key, value, created_at, updated_at

        # 키 컬럼 확인
        key_column = next(col for col in table_info if col["name"] == "key")
        assert key_column["pk"] is True
        assert key_column["type"] == "TEXT"


class TestRedisStorage:
    """Redis 저장소 테스트."""

    def test_redis_import_error(self, mocker: "MockerFixture") -> None:
        """Redis 패키지 없을 때 에러 테스트."""
        # sys.modules에서 redis 모듈을 제거하여 ImportError 시뮬레이션
        import sys
        original_modules = sys.modules.copy()
        if 'redis' in sys.modules:
            del sys.modules['redis']

        # pyconfbox.storage.redis 모듈도 다시 로드해야 함
        if 'pyconfbox.storage.redis' in sys.modules:
            del sys.modules['pyconfbox.storage.redis']

        try:
            from pyconfbox.storage.redis import RedisStorage
            storage = RedisStorage()
            with pytest.raises(StorageError, match="Redis package not found"):
                storage.initialize()
        finally:
            # 원래 모듈 상태 복원
            sys.modules.update(original_modules)

    def test_redis_connection_error(self, mocker: "MockerFixture") -> None:
        """Redis 연결 에러 테스트."""
        # redis 모듈 모킹
        mock_redis_module = mocker.MagicMock()
        mock_redis_class = mocker.MagicMock()
        mock_client = mocker.MagicMock()

        mock_redis_module.Redis = mock_redis_class
        mock_redis_class.return_value = mock_client
        mock_client.ping.side_effect = Exception("Connection failed")

        # sys.modules에 모킹된 redis 모듈 추가
        mocker.patch.dict('sys.modules', {'redis': mock_redis_module})

        storage = RedisStorage()
        with pytest.raises(StorageError, match="Failed to connect to Redis"):
            storage.initialize()

    def test_redis_basic_operations(self, mocker: "MockerFixture") -> None:
        """Redis 기본 동작 테스트."""
        # redis 모듈 모킹
        mock_redis_module = mocker.MagicMock()
        mock_redis_class = mocker.MagicMock()
        mock_client = mocker.MagicMock()

        mock_redis_module.Redis = mock_redis_class
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.get.return_value = "test_value"
        mock_client.set.return_value = True

        # sys.modules에 모킹된 redis 모듈 추가
        mocker.patch.dict('sys.modules', {'redis': mock_redis_module})

        storage = RedisStorage()
        storage.initialize()

        # Set
        storage.set("test_key", "test_value")
        mock_client.set.assert_called_with("pyconfbox:test_key", "test_value")

        # Get
        result = storage.get("test_key")
        assert result == "test_value"
        mock_client.get.assert_called_with("pyconfbox:test_key")

    def test_redis_serialization(self, mocker: "MockerFixture") -> None:
        """Redis 직렬화 테스트."""
        # redis 모듈 모킹
        mock_redis_module = mocker.MagicMock()
        mock_redis_class = mocker.MagicMock()
        mock_client = mocker.MagicMock()

        mock_redis_module.Redis = mock_redis_class
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        # sys.modules에 모킹된 redis 모듈 추가
        mocker.patch.dict('sys.modules', {'redis': mock_redis_module})

        storage = RedisStorage()
        storage.initialize()

        # 복잡한 객체 저장
        test_data = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        storage.set("complex", test_data)

        expected_json = json.dumps(test_data, ensure_ascii=False)
        mock_client.set.assert_called_with("pyconfbox:complex", expected_json)

    def test_redis_prefix(self, mocker: "MockerFixture") -> None:
        """Redis 키 접두어 테스트."""
        # redis 모듈 모킹
        mock_redis_module = mocker.MagicMock()
        mock_redis_class = mocker.MagicMock()
        mock_client = mocker.MagicMock()

        mock_redis_module.Redis = mock_redis_class
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        # sys.modules에 모킹된 redis 모듈 추가
        mocker.patch.dict('sys.modules', {'redis': mock_redis_module})

        storage = RedisStorage(prefix="myapp:")
        storage.initialize()

        storage.set("test_key", "test_value")
        mock_client.set.assert_called_with("myapp:test_key", "test_value")


class TestConfigWithNewStorages:
    """새로운 저장소들과 Config 클래스 통합 테스트."""

    def test_config_with_json_storage(self) -> None:
        """Config와 JSON 저장소 통합 테스트."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            storage = JSONStorage(str(file_path))

            config = Config(default_storage=storage)

            # 설정 저장
            config.set("app_name", "test_app")
            config.set("debug", True)
            config.set("port", 8080)

            # 설정 조회
            assert config.get("app_name") == "test_app"
            assert config.get("debug") is True
            assert config.get("port") == 8080

            # 파일 확인
            assert file_path.exists()

    def test_config_with_sqlite_storage(self) -> None:
        """Config와 SQLite 저장소 통합 테스트."""
        storage = SQLiteStorage()
        config = Config(default_storage=storage)

        # 설정 저장
        config.set("database_url", "sqlite:///app.db")
        config.set("max_connections", 10)

        # 설정 조회
        assert config.get("database_url") == "sqlite:///app.db"
        assert config.get("max_connections") == 10

    def test_config_multiple_storages(self) -> None:
        """Config에서 여러 저장소 사용 테스트."""
        # 메모리 저장소 (기본)
        from pyconfbox import MemoryStorage
        memory_storage = MemoryStorage()

        # SQLite 저장소 (보조)
        sqlite_storage = SQLiteStorage()

        config = Config(
            default_storage=memory_storage,
            fallback_storage=sqlite_storage
        )

        # 기본 저장소에 저장
        config.set("temp_key", "temp_value")
        assert config.get("temp_key") == "temp_value"

        # 보조 저장소에 직접 저장
        sqlite_storage.initialize()
        sqlite_storage.set("persistent_key", "persistent_value")

        # fallback에서 조회되는지 확인 (기본 저장소에 없는 경우)
        # 이 기능은 Config 클래스에서 구현되어야 함
