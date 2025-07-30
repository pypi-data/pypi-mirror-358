
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import discordailib

class TestDiscordAI:
    """Test cases for Discord AI Library"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_bot = Mock()
        self.ai = discordailib.DiscordAI(
            bot=self.mock_bot,
            model=discordailib.AIModel.DEEPSEEK,
            aifeature=discordailib.AIFeature.ALL,
            prefix="!",
            slash=True
        )
    
    def test_initialization(self):
        """Test DiscordAI initialization"""
        assert self.ai.model == discordailib.AIModel.DEEPSEEK
        assert self.ai.aifeature == discordailib.AIFeature.ALL
        assert self.ai.prefix == "!"
        assert self.ai.slash_enabled == True
    
    def test_model_mapping(self):
        """Test model mapping"""
        expected_mappings = {
            discordailib.AIModel.DEEPSEEK: "deepseek-v3",
            discordailib.AIModel.GROK: "grok-3-mini",
            discordailib.AIModel.OPENAI: "gpt-4.1"
        }
        assert self.ai.model_mapping == expected_mappings
    
    def test_get_model_info(self):
        """Test get_model_info method"""
        info = self.ai.get_model_info()
        expected_info = {
            "model": discordailib.AIModel.DEEPSEEK.value,
            "features": discordailib.AIFeature.ALL.value,
            "prefix": "!",
            "slash_commands": True,
            "text_enabled": True,
            "image_enabled": True
        }
        assert info == expected_info
    
    def test_text_only_mode(self):
        """Test text-only mode configuration"""
        ai_text_only = discordailib.DiscordAI(
            bot=self.mock_bot,
            aifeature=discordailib.AIFeature.TEXT_ONLY
        )
        info = ai_text_only.get_model_info()
        assert info["text_enabled"] == True
        assert info["image_enabled"] == False
    
    def test_image_only_mode(self):
        """Test image-only mode configuration"""
        ai_image_only = discordailib.DiscordAI(
            bot=self.mock_bot,
            aifeature=discordailib.AIFeature.IMAGE_ONLY
        )
        info = ai_image_only.get_model_info()
        assert info["text_enabled"] == False
        assert info["image_enabled"] == True
