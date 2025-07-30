from typing import List, Dict, Any, Optional
from .regex import RegexFilter
from .semantic import SemanticCheck
from .multiturn import MultiTurnCheck

class SecurityChecks:
    """
    Implements various security checks for message validation.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize security checks with configuration.
        
        Args:
            config_path: Path to configuration directory
        """
        self.regex_filter = RegexFilter(config_path)
        self.semantic_check = SemanticCheck(config_path)
        self.multi_turn_check = MultiTurnCheck(config_path)
        
    async def check_message(
        self,
        message: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run all security checks on a message.
        
        Args:
            message: The message to check
            history: Previous messages for context
            
        Returns:
            Dict containing:
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with check results
        """
        # Run regex check
        regex_result = await self.regex_filter.check(message)
        if regex_result["blocked"]:
            return regex_result
            
        # Run semantic check
        semantic_result = await self.semantic_check.check(message)
        if semantic_result["blocked"]:
            return semantic_result
            
        # Run multi-turn check
        multi_turn_result = await self.multi_turn_check.check(message, history)
        if multi_turn_result["blocked"]:
            return multi_turn_result
            
        # All checks passed
        return {
            "blocked": False,
            "details": {
                "regex_check": regex_result["details"],
                "semantic_check": semantic_result["details"],
                "multi_turn_check": multi_turn_result["details"]
            }
        } 