from typing import Dict, Any, List, Optional
import yaml
import os

class MultiTurnCheck:
    """
    Implements multi-turn conversation security checks.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize multi-turn check with configuration.
        
        Args:
            config_path: Path to configuration directory
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load multi-turn check configuration.
        """
        config_file = os.path.join(config_path, "security.yml")
        if not os.path.exists(config_file):
            return {
                "max_history": 5,
                "multi_turn_patterns": {
                    "role_switch": ["user", "assistant", "user"],
                    "repetitive": 3
                }
            }
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            
        return config.get("multi_turn_check", {
            "max_history": 5,
            "multi_turn_patterns": {
                "role_switch": ["user", "assistant", "user"],
                "repetitive": 3
            }
        })
        
    async def check(self, message: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check message in context of conversation history.
        
        Args:
            message: Current message to check
            history: Previous messages in conversation
            
        Returns:
            Dict containing:
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with check results
        """
        # Check for role switching attempts
        if len(history) >= 2:
            last_roles = [msg.get("role", "") for msg in history[-2:]]
            if last_roles == self.config["multi_turn_patterns"]["role_switch"]:
                return {
                    "blocked": True,
                    "reason": "Suspicious role switching pattern detected",
                    "details": {
                        "pattern": "role_switch",
                        "roles": last_roles
                    }
                }
        
        # Check for repetitive messages
        if len(history) >= self.config["multi_turn_patterns"]["repetitive"]:
            recent_messages = [msg.get("content", "") for msg in history[-self.config["multi_turn_patterns"]["repetitive"]:]]
            if len(set(recent_messages)) == 1:
                return {
                    "blocked": True,
                    "reason": "Repetitive message pattern detected",
                    "details": {
                        "pattern": "repetitive",
                        "count": len(recent_messages)
                    }
                }
        
        # Check for suspicious patterns in current message
        content = message.get("content", "").lower()
        if "ignore previous instructions" in content or "you are now" in content:
            return {
                "blocked": True,
                "reason": "Attempt to modify system behavior detected",
                "details": {
                    "pattern": "system_modification",
                    "content": content
                }
            }
        
        return {
            "blocked": False,
            "details": {
                "history_length": len(history),
                "last_roles": [msg.get("role", "") for msg in history[-2:]] if history else []
            }
        } 