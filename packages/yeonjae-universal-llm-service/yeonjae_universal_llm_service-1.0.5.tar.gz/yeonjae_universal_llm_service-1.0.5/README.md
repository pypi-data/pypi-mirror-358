# Universal LLM Service

Universal LLM service supporting OpenAI, Anthropic, and local models for code analysis and summarization.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, Azure OpenAI, Google, and local models
- **Async Operations**: Full async/await support for all LLM operations
- **Smart Configuration**: Automatic provider detection and configuration
- **Response Validation**: Built-in response quality validation
- **Rate Limiting**: Intelligent rate limiting and retry mechanisms
- **Type Safety**: Complete type annotations with mypy support
- **Extensible Design**: Easy to add new LLM providers

## Installation

```bash
# Basic installation
pip install yeonjae-universal-llm-service

# With OpenAI support
pip install yeonjae-universal-llm-service[openai]

# With Anthropic support
pip install yeonjae-universal-llm-service[anthropic]

# With all providers
pip install yeonjae-universal-llm-service[all]
```

## Quick Start

```python
import asyncio
from yeonjae_universal_llm_service import LLMService, LLMInput, LLMProvider, ModelConfig

async def main():
    # Initialize service
    service = LLMService()
    
    # Create input
    input_data = LLMInput(
        prompt="Analyze this code and provide insights",
        llm_provider=LLMProvider.OPENAI,
        model_config=ModelConfig(model="gpt-4", temperature=0.3)
    )
    
    # Generate summary
    result = await service.generate_summary(input_data)
    print(f"Summary: {result.summary}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Tokens used: {result.metadata.total_tokens}")

asyncio.run(main())
```

## Configuration

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Supported Providers

- **OpenAI**: GPT-3.5, GPT-4, and newer models
- **Anthropic**: Claude 3 family (Haiku, Sonnet, Opus)
- **Azure OpenAI**: Enterprise OpenAI deployment
- **Google**: Gemini and PaLM models
- **Local**: Custom local model integration

## License

MIT License
