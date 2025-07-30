"""
LLMService 모듈의 예외 클래스

LLM 서비스와 관련된 모든 예외를 정의합니다.
"""


class LLMServiceException(Exception):
    """LLMService 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class UnsupportedProviderException(LLMServiceException):
    """지원하지 않는 LLM 제공자인 경우"""
    def __init__(self, provider: str):
        message = f"Unsupported LLM provider: {provider}"
        super().__init__(message, {
            "provider": provider,
            "supported_providers": ["openai", "anthropic", "local", "azure_openai"]
        })


class APICallFailedException(LLMServiceException):
    """LLM API 호출이 실패한 경우"""
    def __init__(self, provider: str, error: Exception, status_code: int = None):
        message = f"LLM API call failed for {provider}"
        super().__init__(message, {
            "provider": provider,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "status_code": status_code
        })


class TokenLimitExceededException(LLMServiceException):
    """토큰 제한을 초과한 경우"""
    def __init__(self, current_tokens: int, limit: int, provider: str):
        message = f"Token limit exceeded for {provider}: {current_tokens} > {limit}"
        super().__init__(message, {
            "current_tokens": current_tokens,
            "limit": limit,
            "provider": provider,
            "excess": current_tokens - limit
        })


class ResponseValidationException(LLMServiceException):
    """LLM 응답 검증에 실패한 경우"""
    def __init__(self, reason: str, response_data: dict = None):
        message = f"Response validation failed: {reason}"
        super().__init__(message, {
            "reason": reason,
            "response_data": response_data
        })


class RateLimitException(LLMServiceException):
    """API 요청 제한에 걸린 경우"""
    def __init__(self, provider: str, retry_after: int = None):
        message = f"Rate limit exceeded for {provider}"
        super().__init__(message, {
            "provider": provider,
            "retry_after": retry_after
        })


class InvalidModelConfigException(LLMServiceException):
    """잘못된 모델 설정인 경우"""
    def __init__(self, config_field: str, value: str, reason: str):
        message = f"Invalid model config - {config_field}: {reason}"
        super().__init__(message, {
            "config_field": config_field,
            "value": value,
            "reason": reason
        })


class ProviderNotConfiguredException(LLMServiceException):
    """LLM 제공자가 설정되지 않은 경우"""
    def __init__(self, provider: str):
        message = f"Provider not configured: {provider}"
        super().__init__(message, {
            "provider": provider
        })


class TimeoutException(LLMServiceException):
    """요청 시간 초과인 경우"""
    def __init__(self, provider: str, timeout: int):
        message = f"Request timeout for {provider} after {timeout} seconds"
        super().__init__(message, {
            "provider": provider,
            "timeout": timeout
        }) 