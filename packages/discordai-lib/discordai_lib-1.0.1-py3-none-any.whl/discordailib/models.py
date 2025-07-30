
from enum import Enum

class AIModel(Enum):
    """Available AI models on Pollination.ai"""
    DEEPSEEK = "deepseek-v3"
    GROK = "grok-3-mini"
    OPENAI = "gpt-4.1"

class AIFeature(Enum):
    """AI feature modes"""
    TEXT_ONLY = "textonly"
    IMAGE_ONLY = "imageonly"
    ALL = "all"
