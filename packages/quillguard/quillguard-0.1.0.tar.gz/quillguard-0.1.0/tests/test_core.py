import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from quillguard import QuillGuardSDK, Message

@pytest.fixture
def mock_guardrail_manager():
    with patch('duoguard_nemo.guardrails.manager.GuardrailManager') as mock:
        instance = mock.return_value
        instance.check_message = AsyncMock(return_value={"blocked": False})
        yield instance

@pytest.fixture
def mock_content_generator():
    with patch('duoguard_nemo.generation.openai.OpenAIGenerator') as mock:
        instance = mock.return_value
        instance.generate = AsyncMock(return_value="Generated content")
        yield instance

@pytest.fixture
def mock_security_logger():
    with patch('duoguard_nemo.logging.security.SecurityLogger') as mock:
        instance = mock.return_value
        instance.log_decision = MagicMock(return_value={"log": "entry"})
        instance.log_error = MagicMock(return_value={"error": "log"})
        yield instance

@pytest.mark.asyncio
async def test_process_message_success(
    mock_guardrail_manager,
    mock_content_generator,
    mock_security_logger
):
    sdk = QuillGuardSDK()
    messages = [{"role": "user", "content": "Test message"}]
    
    result = await sdk.process_message(messages)
    
    assert result["success"] is True
    assert result["response"] == "Generated content"
    assert "security_log" in result

@pytest.mark.asyncio
async def test_process_message_blocked(
    mock_guardrail_manager,
    mock_content_generator,
    mock_security_logger
):
    mock_guardrail_manager.check_message.return_value = {
        "blocked": True,
        "reason": "Test block"
    }
    
    sdk = QuillGuardSDK()
    messages = [{"role": "user", "content": "Blocked message"}]
    
    result = await sdk.process_message(messages)
    
    assert result["success"] is False
    assert "error" in result
    assert "security_log" in result

@pytest.mark.asyncio
async def test_process_message_error(
    mock_guardrail_manager,
    mock_content_generator,
    mock_security_logger
):
    mock_guardrail_manager.check_message.side_effect = Exception("Test error")
    
    sdk = QuillGuardSDK()
    messages = [{"role": "user", "content": "Error message"}]
    
    result = await sdk.process_message(messages)
    
    assert result["success"] is False
    assert "error" in result
    assert "security_log" in result 