# QuillGuard

A multi-layered security system for LLM applications, built on top of NeMo Guardrails.

## Features

- NeMo Guardrails integration for content filtering
- OpenAI content generation with security checks
- Comprehensive security logging
- Easy-to-use SDK interface
- Configurable security rules

## Installation

```bash
pip install quillguard
```

## Quick Start

```python
import asyncio
from duoguard_nemo import DuoGuardNemoSDK

async def main():
    # Initialize the SDK
    sdk = DuoGuardNemoSDK(
        config_path="config",  # Path to NeMo Guardrails config
        openai_api_key="your-api-key",  # Or use OPENAI_API_KEY env var
        log_path="logs/security.log"
    )
    
    # Process a message
    result = await sdk.process_message(
        messages=[{"role": "user", "content": "Write an article about healthy eating."}],
        system_prompt="You are an AI Article writer..."
    )
    
    if result["success"]:
        print("Generated content:", result["response"])
    else:
        print("Error:", result["error"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### NeMo Guardrails Config

Place your NeMo Guardrails configuration in the `config` directory. The SDK will use this for content filtering.

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional if provided during initialization)

## Security Logging

Security decisions and events are logged to `logs/security.log` by default. Each log entry includes:
- Timestamp
- Event type
- Message content
- Decision details
- Error information (if any)

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 