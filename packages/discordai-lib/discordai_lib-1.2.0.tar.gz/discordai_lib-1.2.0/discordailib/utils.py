
import asyncio
from typing import List, Dict, Any

class AIUtils:
    """Utility functions for Discord AI Library"""
    
    @staticmethod
    def chunk_text(text: str, max_length: int = 2000) -> List[str]:
        """Split text into Discord-friendly chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.rstrip())
        
        return chunks
    
    @staticmethod
    def format_ai_response(response: str, model: str) -> str:
        """Format AI response with model info"""
        return f"🤖 **{model}**: {response}"
    
    @staticmethod
    def create_error_embed(error_message: str) -> Dict[str, Any]:
        """Create error embed for Discord"""
        return {
            "title": "❌ AI Error",
            "description": error_message,
            "color": 0xff0000
        }
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> Dict[str, Any]:
        """Create success embed for Discord"""
        return {
            "title": f"✅ {title}",
            "description": description,
            "color": 0x00ff00
        }
