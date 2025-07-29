"""PyConfBox 타입 시스템."""

import json
from enum import Enum
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, Field, field_validator


class ConfigScope(str, Enum):
    """설정 범위(scope) 열거형."""

    ENV = "env"                    # 환경변수
    GLOBAL = "global"              # 글로벌변수
    LOCAL = "local"                # 로컬변수
    SYSTEM = "system"              # 시스템변수
    SECRET = "secret"              # 비밀변수
    DJANGO = "django"              # Django 설정


class ConfigValue(BaseModel):
    """설정 값을 나타내는 모델."""

    key: str = Field(..., description="설정 키")
    value: Any = Field(..., description="설정 값")
    scope: ConfigScope = Field(default=ConfigScope.GLOBAL, description="설정 범위")
    data_type: Optional[Type] = Field(default=None, description="데이터 타입")
    immutable: bool = Field(default=False, description="불변 여부")
    storage: Optional[str] = Field(default=None, description="저장소 타입")
    created_at: Optional[str] = Field(default=None, description="생성 시간")
    updated_at: Optional[str] = Field(default=None, description="수정 시간")

    model_config = {
        "arbitrary_types_allowed": True,
        "use_enum_values": True
    }

    @field_validator('scope')
    @classmethod
    def validate_scope(cls, v: Union[str, ConfigScope]) -> ConfigScope:
        """
        범위 값을 검증합니다.

        Args:
            v: 범위 값

        Returns:
            검증된 ConfigScope

        Raises:
            ValueError: 잘못된 범위 값
        """
        if isinstance(v, str):
            try:
                return ConfigScope(v)
            except ValueError:
                valid_scopes = [scope.value for scope in ConfigScope]
                raise ValueError(f"Invalid scope '{v}'. Valid scopes: {valid_scopes}")
        return v

    def validate_type(self) -> bool:
        """
        값의 타입을 검증합니다.

        Returns:
            타입이 올바른지 여부
        """
        if self.data_type is None:
            return True

        # 이미 올바른 타입인 경우
        if isinstance(self.value, self.data_type):
            return True

        try:
            # 타입 변환이 가능한지 확인
            if self.data_type is bool and isinstance(self.value, str):
                return self.value.lower() in ('true', 'false', '1', '0', 'yes', 'no')
            elif self.data_type is int and isinstance(self.value, str):
                int(self.value)
                return True
            elif self.data_type is float and isinstance(self.value, str):
                float(self.value)
                return True
            elif self.data_type is list and isinstance(self.value, str):
                return True  # 콤마 구분 문자열은 항상 리스트로 변환 가능
            elif self.data_type is dict and isinstance(self.value, str):
                json.loads(self.value)
                return True
            else:
                # 기타 타입 변환 시도
                self.data_type(self.value)
                return True
        except (TypeError, ValueError, json.JSONDecodeError):
            return False

    def convert_type(self) -> Any:
        """
        값을 지정된 타입으로 변환합니다.

        Returns:
            변환된 값

        Raises:
            ValueError: 타입 변환 실패
        """
        if self.data_type is None:
            return self.value

        if isinstance(self.value, self.data_type):
            return self.value

        try:
            if self.data_type is bool and isinstance(self.value, str):
                return self.value.lower() in ('true', '1', 'yes')
            elif self.data_type is list and isinstance(self.value, str):
                # 문자열을 리스트로 변환 (콤마 구분)
                return [item.strip() for item in self.value.split(',')]
            elif self.data_type is dict and isinstance(self.value, str):
                # JSON 문자열을 딕셔너리로 변환
                return json.loads(self.value)
            else:
                return self.data_type(self.value)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot convert '{self.value}' to {self.data_type.__name__}: {e}")


class ConfigMetadata(BaseModel):
    """설정 메타데이터."""

    total_configs: int = Field(default=0, description="총 설정 개수")
    scopes: Dict[str, int] = Field(default_factory=dict, description="범위별 설정 개수")
    storages: Dict[str, int] = Field(default_factory=dict, description="저장소별 설정 개수")
    immutable_count: int = Field(default=0, description="불변 설정 개수")
    is_released: bool = Field(default=False, description="릴리즈 여부")

    def add_config(self, config_value: ConfigValue) -> None:
        """
        설정 추가 시 메타데이터를 업데이트합니다.

        Args:
            config_value: 추가된 설정 값
        """
        self.total_configs += 1

        # 범위별 카운트 업데이트
        scope_str = config_value.scope.value
        self.scopes[scope_str] = self.scopes.get(scope_str, 0) + 1

        # 저장소별 카운트 업데이트
        if config_value.storage:
            self.storages[config_value.storage] = self.storages.get(config_value.storage, 0) + 1

        # 불변 설정 카운트 업데이트
        if config_value.immutable:
            self.immutable_count += 1

    def remove_config(self, config_value: ConfigValue) -> None:
        """
        설정 제거 시 메타데이터를 업데이트합니다.

        Args:
            config_value: 제거된 설정 값
        """
        self.total_configs = max(0, self.total_configs - 1)

        # 범위별 카운트 업데이트
        scope_str = config_value.scope.value
        if scope_str in self.scopes:
            self.scopes[scope_str] = max(0, self.scopes[scope_str] - 1)
            if self.scopes[scope_str] == 0:
                del self.scopes[scope_str]

        # 저장소별 카운트 업데이트
        if config_value.storage and config_value.storage in self.storages:
            self.storages[config_value.storage] = max(0, self.storages[config_value.storage] - 1)
            if self.storages[config_value.storage] == 0:
                del self.storages[config_value.storage]

        # 불변 설정 카운트 업데이트
        if config_value.immutable:
            self.immutable_count = max(0, self.immutable_count - 1)


# 타입 별칭
ConfigDict = Dict[str, ConfigValue]
ScopeDict = Dict[ConfigScope, ConfigDict]
