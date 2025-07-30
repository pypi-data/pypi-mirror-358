"""
LLMService 모듈의 데이터 모델

상세설계서에 정의된 Input/Output 데이터 구조를 정의합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class LLMProvider(Enum):
    """LLM 제공자"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"


@dataclass
class ModelConfig:
    """모델 설정"""
    model: str  # "gpt-4", "claude-3-sonnet", etc.
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    
    def __post_init__(self):
        # 온도 값 검증
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        # top_p 값 검증
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")


@dataclass
class LLMInput:
    """LLM 입력 데이터 (상세설계서 Input 데이터)"""
    prompt: str
    llm_provider: LLMProvider
    model_config: ModelConfig
    context_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.prompt or not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")


@dataclass
class LLMResponseMetadata:
    """LLM 응답 메타데이터"""
    token_usage: Dict[str, int]  # {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
    response_time: float  # 응답 시간 (초)
    model_used: str
    provider: str
    cost_estimate: float = 0.0
    request_id: Optional[str] = None
    finish_reason: Optional[str] = None
    
    @property
    def total_tokens(self) -> int:
        """총 토큰 수"""
        return self.token_usage.get("total_tokens", 0)
    
    @property
    def prompt_tokens(self) -> int:
        """프롬프트 토큰 수"""
        return self.token_usage.get("prompt_tokens", 0)
    
    @property
    def completion_tokens(self) -> int:
        """완성 토큰 수"""
        return self.token_usage.get("completion_tokens", 0)


@dataclass
class LLMResult:
    """LLM 결과 데이터 (상세설계서 Output 데이터)"""
    summary: str
    metadata: LLMResponseMetadata
    confidence_score: Optional[float] = None
    raw_response: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """응답 유효성 확인"""
        return bool(self.summary and self.summary.strip())
    
    @property
    def word_count(self) -> int:
        """단어 수"""
        return len(self.summary.split())
    
    @property
    def character_count(self) -> int:
        """문자 수"""
        return len(self.summary)


@dataclass
class ProviderConfig:
    """제공자별 설정"""
    provider: LLMProvider
    api_key: str
    base_url: Optional[str] = None
    organization: Optional[str] = None
    api_version: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("API key is required")


@dataclass
class RateLimitInfo:
    """API 제한 정보"""
    requests_per_minute: int
    tokens_per_minute: int
    requests_remaining: Optional[int] = None
    tokens_remaining: Optional[int] = None
    reset_time: Optional[datetime] = None
    
    @property
    def is_rate_limited(self) -> bool:
        """제한 상태 확인"""
        return (self.requests_remaining is not None and self.requests_remaining <= 0) or \
               (self.tokens_remaining is not None and self.tokens_remaining <= 0)


@dataclass
class LLMCapabilities:
    """LLM 능력 정보"""
    max_context_length: int
    supports_function_calling: bool = False
    supports_streaming: bool = False
    supports_system_messages: bool = True
    supported_languages: List[str] = field(default_factory=lambda: ["korean", "english"])
    
    def can_handle_prompt(self, prompt_length: int) -> bool:
        """프롬프트 처리 가능 여부"""
        return prompt_length <= self.max_context_length


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        """문제가 있는지 확인"""
        return len(self.issues) > 0
    
    @property
    def has_warnings(self) -> bool:
        """경고가 있는지 확인"""
        return len(self.warnings) > 0


@dataclass
class LLMRequest:
    """LLM 요청 정보"""
    request_id: str
    timestamp: datetime
    provider: LLMProvider
    model: str
    prompt_length: int
    estimated_tokens: int
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


@dataclass
class LLMResponse:
    """LLM 응답 정보"""
    request_id: str
    response_text: str
    metadata: LLMResponseMetadata
    validation_result: Optional[ValidationResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_successful(self) -> bool:
        """성공적인 응답인지 확인"""
        return bool(self.response_text and 
                   (self.validation_result is None or self.validation_result.is_valid))


@dataclass
class PromptOptimization:
    """프롬프트 최적화 정보"""
    original_length: int
    optimized_length: int
    optimization_applied: List[str] = field(default_factory=list)
    tokens_saved: int = 0
    
    @property
    def compression_ratio(self) -> float:
        """압축 비율"""
        if self.original_length == 0:
            return 0.0
        return 1.0 - (self.optimized_length / self.original_length) 