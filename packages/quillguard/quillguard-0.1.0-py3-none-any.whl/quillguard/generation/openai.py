from typing import List, Dict, Any, Optional
import os
from openai import OpenAI
from ..logging.security import SecurityLogger

class OpenAIGenerator:
    """
    Handles content generation using OpenAI's API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (optional, can use env var)
        """
        self.client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY")
        )
        self.logger = SecurityLogger()
        
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Generate content using OpenAI's API.
        
        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            model: OpenAI model to use
            
        Returns:
            Generated content as string
        """
        try:
            # Prepare messages with system prompt if provided
            api_messages = []
            if system_prompt:
                api_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            api_messages.extend(messages)
            
            # Generate completion
            completion = self.client.chat.completions.create(
                model=model,
                messages=api_messages
            )
            
            # Log successful generation
            self.logger.log_generation(
                messages=messages,
                response=completion.choices[0].message.content
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            # Log generation error
            self.logger.log_error(
                message=messages[-1] if messages else None,
                error=f"Generation error: {str(e)}"
            )
            raise 