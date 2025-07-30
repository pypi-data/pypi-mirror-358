"""
Universal LLM Service 기본 테스트
"""

import pytest
import asyncio
from yeonjae_universal_llm_service import (
    LLMService,
    LLMInput,
    LLMProvider,
    ModelConfig,
    __version__
)


def test_version():
    """버전 정보 테스트"""
    assert __version__ == "1.0.0"


def test_import():
    """패키지 import 테스트"""
    from yeonjae_universal_llm_service import (
        LLMService, LLMInput, LLMResult, LLMProvider, 
        ModelConfig, LLMResponseMetadata
    )
    assert LLMService is not None
    assert LLMInput is not None
    assert LLMProvider is not None


def test_service_creation():
    """LLMService 인스턴스 생성 테스트"""
    service = LLMService()
    assert service is not None
    assert service.default_provider == LLMProvider.OPENAI


def test_model_config():
    """ModelConfig 생성 및 검증 테스트"""
    config = ModelConfig(model="gpt-4", temperature=0.3)
    assert config.model == "gpt-4"
    assert config.temperature == 0.3
    assert config.max_tokens is None


def test_model_config_validation():
    """ModelConfig 유효성 검증 테스트"""
    # 올바른 설정
    config = ModelConfig(model="gpt-4", temperature=0.5)
    assert config.temperature == 0.5
    
    # 잘못된 온도 값
    with pytest.raises(ValueError):
        ModelConfig(model="gpt-4", temperature=3.0)  # > 2.0
    
    with pytest.raises(ValueError):
        ModelConfig(model="gpt-4", temperature=-0.1)  # < 0.0


def test_llm_input():
    """LLMInput 생성 테스트"""
    config = ModelConfig(model="gpt-4")
    input_data = LLMInput(
        prompt="Test prompt",
        llm_provider=LLMProvider.OPENAI,
        model_config=config
    )
    assert input_data.prompt == "Test prompt"
    assert input_data.llm_provider == LLMProvider.OPENAI


def test_llm_input_validation():
    """LLMInput 유효성 검증 테스트"""
    config = ModelConfig(model="gpt-4")
    
    # 빈 프롬프트
    with pytest.raises(ValueError):
        LLMInput(
            prompt="",
            llm_provider=LLMProvider.OPENAI,
            model_config=config
        )
    
    # 공백만 있는 프롬프트
    with pytest.raises(ValueError):
        LLMInput(
            prompt="   ",
            llm_provider=LLMProvider.OPENAI,
            model_config=config
        )


@pytest.mark.asyncio
async def test_local_summary_generation():
    """로컬 LLM 요약 생성 테스트"""
    service = LLMService()
    
    config = ModelConfig(model="local-model")
    input_data = LLMInput(
        prompt="Test prompt for local analysis",
        llm_provider=LLMProvider.LOCAL,
        model_config=config
    )
    
    result = await service.generate_summary(input_data)
    
    assert result is not None
    assert result.summary is not None
    assert len(result.summary) > 0
    assert result.metadata is not None
    assert result.metadata.provider == "local"
    assert result.confidence_score == 0.6


def test_provider_management():
    """Provider 관리 기능 테스트"""
    service = LLMService()
    
    # 사용 가능한 provider 확인
    available = service.get_available_providers()
    assert isinstance(available, list)
    
    # LOCAL provider는 항상 사용 가능
    assert service.is_provider_configured(LLMProvider.LOCAL)
