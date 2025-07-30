import re
import yaml
from typing import Dict, Any, List
import os

class RegexFilter:
    """
    Implements regex-based security checks.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize regex filter with patterns from config.
        
        Args:
            config_path: Path to configuration directory
        """
        self.patterns = self._load_patterns(config_path)
        
    def _load_patterns(self, config_path: str) -> List[re.Pattern]:
        """
        Load regex patterns from config file.
        """
        config_file = os.path.join(config_path, "security.yml")
        if not os.path.exists(config_file):
            return []
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            
        patterns = config.get("regex_patterns", [])
        return [re.compile(pattern["pattern"], re.IGNORECASE) for pattern in patterns]
        
    async def check(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check message against regex patterns.
        
        Args:
            message: The message to check
            
        Returns:
            Dict containing:
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with matched patterns
        """
        content = message.get("content", "")
        matched_patterns = []
        
        for pattern in self.patterns:
            if pattern.search(content):
                matched_patterns.append(pattern.pattern)
                
        if matched_patterns:
            return {
                "blocked": True,
                "reason": "Blocked by regex pattern",
                "details": {
                    "matched_patterns": matched_patterns
                }
            }
            
        return {
            "blocked": False,
            "details": {
                "matched_patterns": []
            }
        } 