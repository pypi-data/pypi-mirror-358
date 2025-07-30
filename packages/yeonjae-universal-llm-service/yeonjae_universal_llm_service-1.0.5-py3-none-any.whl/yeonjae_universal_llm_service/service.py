"""
LLMService 서비스

OpenAI, Anthropic, 로컬 LLM 등 다양한 LLM을 통합 관리하는 메인 서비스입니다.
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any
import os

from .models import (
    LLMInput, LLMResult, LLMProvider, ModelConfig,
    LLMResponseMetadata, ProviderConfig
)
from .exceptions import (
    LLMServiceException, UnsupportedProviderException,
    APICallFailedException, ProviderNotConfiguredException
)

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 서비스"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.default_provider = LLMProvider.OPENAI
        logger.info("LLMService initialized")
    
    def _initialize_providers(self) -> Dict[LLMProvider, ProviderConfig]:
        """제공자별 설정 초기화"""
        providers = {}
        
        # OpenAI 설정
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            providers[LLMProvider.OPENAI] = ProviderConfig(
                provider=LLMProvider.OPENAI,
                api_key=openai_key
            )
        
        # Anthropic 설정
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            providers[LLMProvider.ANTHROPIC] = ProviderConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=anthropic_key
            )
        
        return providers
    
    async def generate_summary(self, input_data: LLMInput) -> LLMResult:
        """주요 요약 생성 메서드"""
        try:
            start_time = time.time()
            
            # Provider Selection
            if input_data.llm_provider not in self.providers:
                if input_data.llm_provider == LLMProvider.LOCAL:
                    return await self._generate_local_summary(input_data)
                else:
                    raise UnsupportedProviderException(input_data.llm_provider.value)
            
            # API Call
            response_text = await self._call_llm_api(input_data)
            
            # Response Processing
            response_time = time.time() - start_time
            metadata = self._create_metadata(input_data, response_time)
            
            # Quality Validation
            validated_response = self._validate_response(response_text)
            
            return LLMResult(
                summary=validated_response,
                metadata=metadata,
                confidence_score=0.85  # 기본 신뢰도
            )
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise APICallFailedException(input_data.llm_provider.value, e)
    
    async def _call_llm_api(self, input_data: LLMInput) -> str:
        """LLM API 호출"""
        provider_config = self.providers[input_data.llm_provider]
        
        if input_data.llm_provider == LLMProvider.OPENAI:
            return await self._call_openai_api(input_data, provider_config)
        elif input_data.llm_provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic_api(input_data, provider_config)
        else:
            raise UnsupportedProviderException(input_data.llm_provider.value)
    
    async def _call_openai_api(self, input_data: LLMInput, 
                              config: ProviderConfig) -> str:
        """OpenAI API 호출"""
        try:
            # 실제 OpenAI API 호출 대신 Mock 응답
            await asyncio.sleep(0.5)  # API 호출 시뮬레이션
            
            return f"""
{input_data.prompt}에 대한 AI 분석 결과:

📊 종합 분석:
- 개발 활동이 활발하게 진행되었습니다.
- 코드 품질이 양호한 수준을 유지하고 있습니다.
- 작업 패턴이 일관성 있게 관리되고 있습니다.

💡 주요 인사이트:
- 효율적인 개발 프로세스가 확인됩니다.
- 지속적인 개선이 이루어지고 있습니다.

🎯 권장사항:
- 현재 수준을 유지하며 점진적 개선을 추천합니다.
            """.strip()
            
        except Exception as e:
            raise APICallFailedException("openai", e)
    
    async def _call_anthropic_api(self, input_data: LLMInput, 
                                 config: ProviderConfig) -> str:
        """Anthropic API 호출"""
        try:
            # 실제 Anthropic API 호출 대신 Mock 응답
            await asyncio.sleep(0.7)  # API 호출 시뮬레이션
            
            return f"""
Claude 분석 결과:

{input_data.prompt}에 대한 상세 분석을 제공합니다.

🔍 분석 요약:
개발자의 활동 패턴과 코드 품질을 종합적으로 분석한 결과, 
전반적으로 우수한 개발 성과를 보이고 있습니다.

📈 성과 지표:
- 생산성: 높음
- 코드 품질: 양호
- 일관성: 우수

💭 개선 제안:
지속적인 발전을 위한 구체적인 방향성을 제시합니다.
            """.strip()
            
        except Exception as e:
            raise APICallFailedException("anthropic", e)
    
    async def _generate_local_summary(self, input_data: LLMInput) -> LLMResult:
        """로컬 LLM을 사용한 요약 생성"""
        try:
            start_time = time.time()
            
            # 간단한 로컬 처리
            summary = f"""
로컬 LLM 분석 결과:

입력된 프롬프트를 분석하여 다음과 같은 요약을 제공합니다:

📋 요약:
- 개발 활동이 정상적으로 수행되었습니다.
- 기본적인 품질 기준을 충족하고 있습니다.

⚠️ 참고:
이 결과는 로컬 처리된 간단한 분석입니다.
            """.strip()
            
            response_time = time.time() - start_time
            
            metadata = LLMResponseMetadata(
                token_usage={"prompt_tokens": 100, "completion_tokens": 150, "total_tokens": 250},
                response_time=response_time,
                model_used="local-model",
                provider="local"
            )
            
            return LLMResult(
                summary=summary,
                metadata=metadata,
                confidence_score=0.6  # 로컬 모델은 낮은 신뢰도
            )
            
        except Exception as e:
            raise APICallFailedException("local", e)
    
    def switch_provider(self, new_provider: LLMProvider):
        """LLM 제공자 동적 변경"""
        if new_provider not in self.providers and new_provider != LLMProvider.LOCAL:
            raise ProviderNotConfiguredException(new_provider.value)
        
        self.default_provider = new_provider
        logger.info(f"Switched to provider: {new_provider.value}")
    
    def validate_response(self, response: str) -> bool:
        """응답 품질 검증"""
        return self._validate_response(response) is not None
    
    def handle_rate_limits(self, provider: LLMProvider) -> int:
        """API 제한 처리"""
        # 간단한 재시도 지연 반환
        return 60  # 60초 대기
    
    def _create_metadata(self, input_data: LLMInput, response_time: float) -> LLMResponseMetadata:
        """메타데이터 생성"""
        estimated_prompt_tokens = len(input_data.prompt.split()) * 1.3
        estimated_completion_tokens = 200  # 기본값
        
        return LLMResponseMetadata(
            token_usage={
                "prompt_tokens": int(estimated_prompt_tokens),
                "completion_tokens": estimated_completion_tokens,
                "total_tokens": int(estimated_prompt_tokens) + estimated_completion_tokens
            },
            response_time=response_time,
            model_used=input_data.model_config.model,
            provider=input_data.llm_provider.value,
            cost_estimate=0.02  # 기본 비용 추정
        )
    
    def _validate_response(self, response: str) -> Optional[str]:
        """응답 검증"""
        if not response or len(response.strip()) < 10:
            return None
        
        # 기본적인 필터링
        if "error" in response.lower() or "failed" in response.lower():
            return None
        
        return response.strip()
    
    def get_available_providers(self) -> List[LLMProvider]:
        """사용 가능한 제공자 목록"""
        available = list(self.providers.keys())
        available.append(LLMProvider.LOCAL)  # 로컬은 항상 사용 가능
        return available
    
    def is_provider_configured(self, provider: LLMProvider) -> bool:
        """제공자 설정 여부 확인"""
        return provider in self.providers or provider == LLMProvider.LOCAL 