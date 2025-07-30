"""
Universal LLM Service

OpenAI, Anthropic, 로컬 LLM 등 다양한 LLM을 통합 관리하는 범용 모듈입니다.
개발자별 코드 분석 및 요약 생성을 수행합니다.

이 모듈은 AI-driven Modular Design 원칙에 따라 설계되었으며,
다른 프로젝트에서도 독립적으로 사용할 수 있습니다.
"""

__version__ = "1.0.0"

from .service import LLMService
from .models import (
    LLMInput,
    LLMResult,
    LLMProvider,
    ModelConfig,
    LLMResponseMetadata,
    ProviderConfig,
    RateLimitInfo,
    LLMCapabilities,
    ValidationResult,
    LLMRequest,
    LLMResponse,
    PromptOptimization
)
from .exceptions import (
    LLMServiceException,
    UnsupportedProviderException,
    APICallFailedException,
    TokenLimitExceededException,
    ResponseValidationException,
    ProviderNotConfiguredException
)

__all__ = [
    '__version__',
    'LLMService',
    'LLMInput',
    'LLMResult',
    'LLMProvider',
    'ModelConfig',
    'LLMResponseMetadata',
    'ProviderConfig',
    'RateLimitInfo',
    'LLMCapabilities',
    'ValidationResult',
    'LLMRequest',
    'LLMResponse',
    'PromptOptimization',
    'LLMServiceException',
    'UnsupportedProviderException',
    'APICallFailedException',
    'TokenLimitExceededException',
    'ResponseValidationException',
    'ProviderNotConfiguredException'
]
