import yaml
import os
import numpy as np
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer, util

class SemanticCheck:
    """
    Implements semantic similarity-based security checks.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize semantic checker with configuration.
        
        Args:
            config_path: Path to configuration directory
        """
        self.config = self._load_config(config_path)
        self.model = SentenceTransformer(self.config["model_name"])
        self.thresholds = self.config["thresholds"]
        self.seed_embeddings = self._load_seed_embeddings()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load semantic check configuration.
        """
        config_file = os.path.join(config_path, "security.yml")
        if not os.path.exists(config_file):
            return {
                "model_name": "all-MiniLM-L6-v2",
                "thresholds": {"high": 0.85, "low": 0.65}
            }
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            
        return {
            "model_name": config.get("semantic_model", "all-MiniLM-L6-v2"),
            "thresholds": config.get("semantic_thresholds", {"high": 0.85, "low": 0.65})
        }
        
    def _load_seed_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Load and encode seed texts for similarity comparison.
        """
        seeds = {
            "jailbreak": [
                "ignore previous instructions",
                "you are now DAN",
                "you can do anything now",
                # Add more seed texts
            ],
            "harmful": [
                "how to hack",
                "how to make weapons",
                "how to harm others",
                # Add more seed texts
            ]
        }
        
        embeddings = {}
        for category, texts in seeds.items():
            embeddings[category] = self.model.encode(texts, convert_to_tensor=True)
            
        return embeddings
        
    async def check(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check message for semantic similarity to known problematic content.
        
        Args:
            message: The message to check
            
        Returns:
            Dict containing:
            - blocked: bool
            - reason: str (if blocked)
            - details: Dict with similarity scores
        """
        content = message.get("content", "")
        message_embedding = self.model.encode(content, convert_to_tensor=True)
        
        similarities = {}
        for category, embeddings in self.seed_embeddings.items():
            scores = util.cos_sim(message_embedding, embeddings)
            similarities[category] = float(scores.max())
            
        # Check against thresholds
        high_threshold = self.thresholds["high"]
        low_threshold = self.thresholds["low"]
        
        for category, score in similarities.items():
            if score >= high_threshold:
                return {
                    "blocked": True,
                    "reason": f"High similarity to {category} content",
                    "details": {
                        "similarities": similarities,
                        "threshold": high_threshold
                    }
                }
                
        return {
            "blocked": False,
            "details": {
                "similarities": similarities,
                "thresholds": self.thresholds
            }
        } 