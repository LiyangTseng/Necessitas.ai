"""
Chat API Router

Provides REST API endpoints for AI-powered chat interactions.
Integrates with Bedrock AgentCore runtime for intelligent responses.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
import httpx
import json
import re

from agents.bedrock_agent.invoke import invoke_agent
from models.chat import ChatMessage, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Put it here as a workaround
def clean_agent_response(response: str) -> str:
    """
    Clean the agent response by removing internal thinking tags and formatting.

    Args:
        response: Raw response from the agent

    Returns:
        Cleaned response ready for display
    """
    if not response:
        return response

    # Remove <thinking>...</thinking> blocks
    response = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL)

    # Remove any remaining <thinking> tags without closing tags
    response = re.sub(r'<thinking>.*$', '', response, flags=re.DOTALL)

    # Clean up extra whitespace and newlines
    response = re.sub(r'\n\s*\n', '\n\n', response)  # Replace multiple newlines with double newlines
    response = response.strip()

    return response

def process_markdown_response(response: str) -> Dict[str, Any]:
    """
    Process markdown in the response and return structured data for frontend rendering.

    Args:
        response: Cleaned response text

    Returns:
        Dictionary with processed content for frontend
    """
    if not response:
        return {"text": "", "hasMarkdown": False}

    # Check if response contains markdown formatting
    has_markdown = bool(re.search(r'\*\*.*?\*\*|^\d+\.|^[-*]', response, re.MULTILINE))

    # For now, return the raw text with markdown indicators
    # The frontend can handle the markdown rendering
    return {
        "text": response,
        "hasMarkdown": has_markdown,
        "markdownContent": response  # Frontend can use this for markdown rendering
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the AI career assistant using Bedrock AgentCore runtime.

    Args:
        request: Chat message and conversation history

    Returns:
        AI assistant response
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")

        # Get raw response from agent
        raw_response = invoke_agent(
            prompt=request.message,
            setup_runtime=False,
            agent_arn="arn:aws:bedrock-agentcore:us-west-2:488234668762:runtime/bedrock_agent-TO4pEH7Avm",
            agent_id="bedrock_agent-TO4pEH7Avm",
            client_id="6riuf44c9oa1vf7ut7t2jukf37"
        )

        # Clean the response (remove thinking tags, etc.)
        cleaned_response = clean_agent_response(raw_response)

        # Process markdown formatting
        processed_response = process_markdown_response(cleaned_response)

        return ChatResponse(
            response=processed_response["text"],
            success=True,
            # Add additional fields for frontend markdown processing
            markdown_content=processed_response.get("markdownContent"),
            has_markdown=processed_response.get("hasMarkdown", False)
        )
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")


@router.get("/chat/health")
async def chat_health_check():
    """Health check for chat service."""
    return {"status": "healthy", "service": "chat_agent"}


@router.post("/chat/test")
async def test_chat():
    """Test endpoint for chat functionality."""
    return {
        "message": "Chat service is working!",
        "status": "ready"
    }
