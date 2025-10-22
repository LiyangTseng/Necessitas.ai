"""
Chat Models

Data models for chat functionality and AI assistant interactions.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessage:
    """Individual chat message model."""
    role: str  # 'user' or 'assistant'
    content: str


@dataclass
class ChatRequest:
    """Request model for chat messages."""
    message: str
    conversation_history: List[ChatMessage] = None

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


@dataclass
class ChatResponse:
    """Response model for chat messages."""
    response: str
    success: bool = True
    error: Optional[str] = None
    markdown_content: Optional[str] = None
    has_markdown: bool = False
