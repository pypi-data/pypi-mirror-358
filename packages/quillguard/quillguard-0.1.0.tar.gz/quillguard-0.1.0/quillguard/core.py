from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .guardrails.manager import GuardrailManager
from .generation.openai import OpenAIGenerator
from .logging.security import SecurityLogger

class Message(BaseModel):
    """Message model for chat interactions."""
    role: str
    content: str

class QuillGuardSDK:
    """
    Main SDK class for QuillGuard security system.
    Orchestrates guardrails, content generation, and security logging.
    """
    
    def __init__(
        self,
        config_path: str = "config",
        openai_api_key: Optional[str] = None,
        log_path: str = "logs/security.log"
    ):
        """
        Initialize the SDK with configuration and clients.
        
        Args:
            config_path: Path to NeMo Guardrails configuration
            openai_api_key: OpenAI API key (optional, can use env var)
            log_path: Path to security log file
        """
        # Initialize components
        self.guardrail_manager = GuardrailManager(config_path)
        self.content_generator = OpenAIGenerator(api_key=openai_api_key)
        self.security_logger = SecurityLogger(log_path)
        
    async def process_message(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a message through the security pipeline.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt for content generation
            
        Returns:
            Dict containing:
            - success: bool
            - response: str (if successful)
            - error: str (if failed)
            - security_log: Dict with security decision details
        """
        try:
            # Get the latest message
            latest_message = messages[-1]
            
            # Process through guardrails
            guardrail_result = await self.guardrail_manager.process_message(
                latest_message,
                messages[:-1]  # Pass history
            )
            
            # Log security decision
            security_log = self.security_logger.log_decision(
                message=latest_message,
                decision=guardrail_result
            )
            
            # If blocked by guardrails
            if guardrail_result.get("blocked", False):
                return {
                    "success": False,
                    "error": guardrail_result.get("reason", "Blocked by guardrails"),
                    "security_log": security_log
                }
            
            # Generate content if allowed
            response = await self.content_generator.generate(
                messages=messages,
                system_prompt=system_prompt
            )
            
            return {
                "success": True,
                "response": response,
                "security_log": security_log
            }
            
        except Exception as e:
            # Log any unexpected errors
            error_log = self.security_logger.log_error(
                message=latest_message,
                error=str(e)
            )
            
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "security_log": error_log
            } 