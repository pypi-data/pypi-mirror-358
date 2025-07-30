from typing import Dict, Any, Optional
import yaml
import os

class ResponseGenerator:
    """
    Generates appropriate responses based on security check results.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize response generator with configuration.
        
        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load response configuration from file.
        """
        config_file = os.path.join(self.config_path, "security.yml")
        if not os.path.exists(config_file):
            return {
                "default_response": "I apologize, but I cannot assist with that request.",
                "error_responses": {
                    "security_violation": "I cannot comply with this request as it may violate security policies.",
                    "invalid_input": "I cannot process this input as it appears to be invalid."
                }
            }
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            
        return config
        
    def generate_response(self,
                         message: Dict[str, Any],
                         check_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate appropriate response based on security check results.
        
        Args:
            message: Original user message
            check_result: Result from security checks
            
        Returns:
            Dict containing:
            - content: str (response text)
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with additional info
        """
        if check_result.get("blocked", False):
            return {
                "content": self.config.get("error_responses", {}).get("security_violation", 
                    "I cannot comply with this request as it may violate security policies."),
                "blocked": True,
                "reason": check_result.get("reason", "Security violation"),
                "details": check_result.get("details", {})
            }
            
        return {
            "content": None,  # Let the content generator handle this
            "blocked": False,
            "details": check_result.get("details", {})
        }
        
    def generate_error_response(self,
                              error_type: str,
                              error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate error response.
        
        Args:
            error_type: Type of error
            error_details: Error details
            
        Returns:
            Dict containing error response
        """
        return {
            "content": self.config.get("error_responses", {}).get(error_type, 
                "An error occurred while processing your request."),
            "blocked": True,
            "reason": f"System error: {error_type}",
            "details": error_details
        } 