"""Config 클래스 테스트."""

from typing import TYPE_CHECKING

import pytest

from pyconfbox import (
    Config,
    ConfigNotFoundError,
    ConfigScope,
    ConfigTypeError,
    ImmutableConfigError,
    ReleasedConfigError,
)

if TYPE_CHECKING:
    pass


class TestConfig:
    """Config 클래스 테스트 케이스."""

    def test_init_default(self) -> None:
        """기본 초기화 테스트."""
        config = Config()
        assert config._default_storage == "memory"
        assert config._fallback_storage is None
        assert len(config._configs) == 0
        assert not config.is_released()

    def test_init_custom_storage(self) -> None:
        """커스텀 저장소 초기화 테스트."""
        config = Config(
            default_storage="environment",
            fallback_storage="memory",
            env_prefix="TEST_"
        )
        assert config._default_storage == "environment"
        assert config._fallback_storage == "memory"

    def test_set_and_get_basic(self) -> None:
        """기본 설정 저장 및 조회 테스트."""
        config = Config()

        # 기본 설정
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

        # 범위 지정
        config.set("env_key", "env_value", scope=ConfigScope.ENV)
        assert config.get("env_key") == "env_value"
        assert config.get("env_key", scope=ConfigScope.ENV) == "env_value"

    def test_set_with_data_type(self) -> None:
        """데이터 타입 지정 테스트."""
        config = Config()

        # 정수 타입
        config.set("port", "8080", data_type=int)
        assert config.get("port") == 8080
        assert isinstance(config.get("port"), int)

        # 불린 타입
        config.set("debug", "true", data_type=bool)
        assert config.get("debug") is True

        config.set("enabled", "false", data_type=bool)
        assert config.get("enabled") is False

        # 리스트 타입
        config.set("hosts", "localhost,127.0.0.1", data_type=list)
        assert config.get("hosts") == ["localhost", "127.0.0.1"]

    def test_get_with_default(self) -> None:
        """기본값 반환 테스트."""
        config = Config()

        # 기본값 반환
        assert config.get("nonexistent", default="default_value") == "default_value"

        # 예외 발생
        with pytest.raises(ConfigNotFoundError):
            config.get("nonexistent")

    def test_immutable_config(self) -> None:
        """불변 설정 테스트."""
        config = Config()

        # 불변 설정 저장
        config.set("secret_key", "secret_value", immutable=True)
        assert config.get("secret_key") == "secret_value"

        # 불변 설정 변경 시도 (예외 발생)
        with pytest.raises(ImmutableConfigError):
            config.set("secret_key", "new_value")

    def test_release_mode(self) -> None:
        """릴리즈 모드 테스트."""
        config = Config()

        # 설정 저장
        config.set("key1", "value1")
        config.set("key2", "value2")

        # 릴리즈
        config.release()
        assert config.is_released()

        # 릴리즈 후 설정 변경 시도 (예외 발생)
        with pytest.raises(ReleasedConfigError):
            config.set("key3", "value3")

        with pytest.raises(ReleasedConfigError):
            config.set("key1", "new_value")

        # 조회는 가능
        assert config.get("key1") == "value1"

    def test_scope_filtering(self) -> None:
        """범위 필터링 테스트."""
        config = Config()

        # 다양한 범위의 설정 저장
        config.set("global_key", "global_value", scope=ConfigScope.GLOBAL)
        config.set("env_key", "env_value", scope=ConfigScope.ENV)
        config.set("secret_key", "secret_value", scope=ConfigScope.SECRET)

        # 범위별 조회
        global_configs = config.get_by_scope(ConfigScope.GLOBAL)
        assert global_configs == {"global_key": "global_value"}

        env_configs = config.get_by_scope(ConfigScope.ENV)
        assert env_configs == {"env_key": "env_value"}

        # 범위 필터링으로 조회
        assert config.get("global_key", scope=ConfigScope.GLOBAL) == "global_value"

        # 잘못된 범위로 조회 (기본값 반환)
        assert config.get("global_key", scope=ConfigScope.ENV, default="not_found") == "not_found"

    def test_update_multiple(self) -> None:
        """다중 설정 업데이트 테스트."""
        config = Config()

        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }

        config.update(data, scope=ConfigScope.GLOBAL)

        assert config.get("key1") == "value1"
        assert config.get("key2") == "value2"
        assert config.get("key3") == "value3"

    def test_delete_config(self) -> None:
        """설정 삭제 테스트."""
        config = Config()

        # 설정 저장
        config.set("temp_key", "temp_value")
        assert config.exists("temp_key")

        # 설정 삭제
        assert config.delete("temp_key") is True
        assert not config.exists("temp_key")

        # 존재하지 않는 설정 삭제
        assert config.delete("nonexistent") is False

    def test_delete_immutable_config(self) -> None:
        """불변 설정 삭제 테스트."""
        config = Config()

        # 불변 설정 저장
        config.set("immutable_key", "immutable_value", immutable=True)

        # 불변 설정 삭제 시도 (예외 발생)
        with pytest.raises(ImmutableConfigError):
            config.delete("immutable_key")

    def test_keys_and_exists(self) -> None:
        """키 목록 및 존재 확인 테스트."""
        config = Config()

        # 설정 저장
        config.set("key1", "value1", scope=ConfigScope.GLOBAL)
        config.set("key2", "value2", scope=ConfigScope.ENV)

        # 모든 키 조회
        all_keys = config.keys()
        assert "key1" in all_keys
        assert "key2" in all_keys

        # 범위별 키 조회
        global_keys = config.keys(scope=ConfigScope.GLOBAL)
        assert global_keys == ["key1"]

        # 존재 확인
        assert config.exists("key1")
        assert config.exists("key2")
        assert not config.exists("nonexistent")

    def test_clear_configs(self) -> None:
        """설정 삭제 테스트."""
        config = Config()

        # 설정 저장
        config.set("key1", "value1", scope=ConfigScope.GLOBAL)
        config.set("key2", "value2", scope=ConfigScope.ENV)
        config.set("key3", "value3", scope=ConfigScope.GLOBAL, immutable=True)

        # 특정 범위 삭제
        config.clear(scope=ConfigScope.GLOBAL)

        # 불변 설정은 삭제되지 않음
        assert config.exists("key3")
        assert config.exists("key2")  # 다른 범위
        assert not config.exists("key1")  # 삭제됨

    def test_metadata(self) -> None:
        """메타데이터 테스트."""
        config = Config()

        # 설정 저장
        config.set("key1", "value1", scope=ConfigScope.GLOBAL, immutable=True)
        config.set("key2", "value2", scope=ConfigScope.ENV)

        metadata = config.get_metadata()
        assert metadata.total_configs == 2
        assert metadata.scopes["global"] == 1
        assert metadata.scopes["env"] == 1
        assert metadata.immutable_count == 1
        assert not metadata.is_released

        # 릴리즈 후
        config.release()
        metadata = config.get_metadata()
        assert metadata.is_released

    def test_type_validation_error(self) -> None:
        """타입 검증 오류 테스트."""
        config = Config()

        # 잘못된 타입으로 설정 시도
        with pytest.raises(ConfigTypeError):
            config.set("port", "invalid_number", data_type=int)

    def test_config_representation(self) -> None:
        """Config 객체의 문자열 표현 테스트."""
        config = Config()
        config.set("test", "value")

        repr_str = repr(config)
        assert "Config(" in repr_str
        assert "configs=1" in repr_str
        assert "released=False" in repr_str
        assert "default_storage='memory'" in repr_str
