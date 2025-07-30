from typing import Dict, Any, Optional, List
import os
from .checks import SecurityChecks
from .regex import RegexFilter
from .semantic import SemanticCheck
from .multiturn import MultiTurnCheck
from ..logging.logger import SecurityLogger
from ..generation.response import ResponseGenerator

class GuardrailManager:
    """
    Main class for managing security guardrails and orchestrating checks.
    """
    
    def __init__(self, config_path: str = "config"):
        """
        Initialize guardrail manager with configuration.
        
        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        os.makedirs(config_path, exist_ok=True)
        
        # Initialize components
        self.regex_filter = RegexFilter(config_path)
        self.semantic_check = SemanticCheck(config_path)
        self.multiturn_check = MultiTurnCheck(config_path)
        self.logger = SecurityLogger()
        self.response_generator = ResponseGenerator(config_path)
        
    async def process_message(self,
                            message: Dict[str, Any],
                            history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Process a message through all security checks.
        
        Args:
            message: The message to process
            history: Previous messages for context
            
        Returns:
            Dict containing:
            - content: str (response text)
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with additional info
        """
        try:
            # Run regex check
            regex_result = await self.regex_filter.check(message)
            if regex_result["blocked"]:
                self.logger.log_violation(
                    message,
                    "regex",
                    regex_result["reason"],
                    regex_result["details"]
                )
                return self.response_generator.generate_response(
                    message,
                    regex_result
                )
                
            # Run semantic check
            semantic_result = await self.semantic_check.check(message)
            if semantic_result["blocked"]:
                self.logger.log_violation(
                    message,
                    "semantic",
                    semantic_result["reason"],
                    semantic_result["details"]
                )
                return self.response_generator.generate_response(
                    message,
                    semantic_result
                )
                
            # Run multi-turn check
            multiturn_result = await self.multiturn_check.check(message, history or [])
            if multiturn_result["blocked"]:
                self.logger.log_violation(
                    message,
                    "multiturn",
                    multiturn_result["reason"],
                    multiturn_result["details"]
                )
                return self.response_generator.generate_response(
                    message,
                    multiturn_result
                )
                
            # Log successful check
            self.logger.log_event(
                "message_processed",
                message,
                {"checks_passed": True}
            )
            
            # Return success result
            return {
                "blocked": False,
                "details": {
                    "regex_check": regex_result["details"],
                    "semantic_check": semantic_result["details"],
                    "multi_turn_check": multiturn_result["details"]
                }
            }
            
        except Exception as e:
            # Log error
            self.logger.log_event(
                "error",
                message,
                {"error": str(e)}
            )
            
            # Return error response
            return self.response_generator.generate_error_response(
                "system_error",
                {"error": str(e)}
            )
            
    def get_recent_violations(self, limit: int = 100) -> list:
        """
        Get recent security violations.
        
        Args:
            limit: Maximum number of violations to return
            
        Returns:
            List of recent violations
        """
        return self.logger.get_recent_violations(limit) 