import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

class SecurityLogger:
    """
    Handles logging of security decisions and events.
    """
    
    def __init__(self, log_path: str = "logs/security.log"):
        """
        Initialize the security logger.
        
        Args:
            log_path: Path to the log file
        """
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        
    def _create_log_entry(
        self,
        event_type: str,
        message: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a standardized log entry.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message.get("content", "") if message else "",
            **kwargs
        }
        return entry
        
    def log_decision(
        self,
        message: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Log a security decision.
        """
        entry = self._create_log_entry(
            event_type="security_decision",
            message=message,
            decision=decision
        )
        self.logger.info(json.dumps(entry))
        return entry
        
    def log_error(
        self,
        message: Optional[Dict[str, Any]],
        error: str
    ) -> Dict[str, Any]:
        """
        Log a security error.
        """
        entry = self._create_log_entry(
            event_type="security_error",
            message=message,
            error=error
        )
        self.logger.error(json.dumps(entry))
        return entry
        
    def log_generation(
        self,
        messages: List[Dict[str, Any]],
        response: str
    ) -> Dict[str, Any]:
        """
        Log a successful content generation.
        """
        entry = self._create_log_entry(
            event_type="content_generation",
            message=messages[-1] if messages else None,
            response=response
        )
        self.logger.info(json.dumps(entry))
        return entry 