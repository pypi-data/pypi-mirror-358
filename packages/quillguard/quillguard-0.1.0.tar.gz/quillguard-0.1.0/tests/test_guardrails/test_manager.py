import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from quillguard.guardrails.manager import GuardrailManager

@pytest.fixture
def mock_rails():
    with patch('quillguard.guardrails.manager.LLMRails') as mock:
        instance = mock.return_value
        instance.generate = AsyncMock(return_value={"blocked": False})
        yield instance

@pytest.fixture
def mock_logger():
    with patch('quillguard.logging.security.SecurityLogger') as mock:
        instance = mock.return_value
        instance.log_error = MagicMock()
        yield instance

@pytest.mark.asyncio
async def test_check_message_allowed(mock_rails, mock_logger):
    manager = GuardrailManager("config")
    message = {"role": "user", "content": "Test message"}
    history = []
    
    result = await manager.check_message(message, history)
    
    assert result["blocked"] is False
    assert "details" in result

@pytest.mark.asyncio
async def test_check_message_blocked(mock_rails, mock_logger):
    mock_rails.generate.return_value = {
        "blocked": True,
        "reason": "Test block"
    }
    
    manager = GuardrailManager("config")
    message = {"role": "user", "content": "Blocked message"}
    history = []
    
    result = await manager.check_message(message, history)
    
    assert result["blocked"] is True
    assert "reason" in result
    assert "details" in result

@pytest.mark.asyncio
async def test_check_message_error(mock_rails, mock_logger):
    mock_rails.generate.side_effect = Exception("Test error")
    
    manager = GuardrailManager("config")
    message = {"role": "user", "content": "Error message"}
    history = []
    
    result = await manager.check_message(message, history)
    
    assert result["blocked"] is True
    assert "error" in result["details"]
    mock_logger.log_error.assert_called_once() 