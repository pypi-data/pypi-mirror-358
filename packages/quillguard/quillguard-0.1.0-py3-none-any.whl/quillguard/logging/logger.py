import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SecurityLogger:
    """
    Handles logging of security events and violations.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize security logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        self.log_file = os.path.join(log_dir, f"security_{datetime.now().strftime('%Y%m%d')}.log")
        self.file_handler = logging.FileHandler(self.log_file)
        self.file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        # Set up logger
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.file_handler)
        
    def log_violation(self, 
                     message: Dict[str, Any],
                     check_type: str,
                     reason: str,
                     details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a security violation.
        
        Args:
            message: The message that triggered the violation
            check_type: Type of check that failed (e.g. "regex", "semantic")
            reason: Reason for the violation
            details: Additional details about the violation
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "violation",
            "check_type": check_type,
            "reason": reason,
            "message": message,
            "details": details or {}
        }
        
        self.logger.warning(json.dumps(log_entry))
        
    def log_event(self,
                 event_type: str,
                 message: Dict[str, Any],
                 details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a general security event.
        
        Args:
            event_type: Type of event
            message: Related message
            details: Additional event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "event",
            "event_type": event_type,
            "message": message,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(log_entry))
        
    def get_recent_violations(self, limit: int = 100) -> list:
        """
        Get recent security violations from the log file.
        
        Args:
            limit: Maximum number of violations to return
            
        Returns:
            List of recent violations
        """
        violations = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if '"type": "violation"' in line:
                        try:
                            violation = json.loads(line.split(" - ")[-1])
                            violations.append(violation)
                        except json.JSONDecodeError:
                            continue
                            
            return violations[-limit:]
        except FileNotFoundError:
            return [] 