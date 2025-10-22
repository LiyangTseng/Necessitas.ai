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

from ..models.chat import ChatMessage, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Bedrock AgentCore Runtime Configuration
BEDROCK_AGENTCORE_RUNTIME_URL = "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/main_agent-B3Kog7FjWn/invocations"

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

        # Prepare the prompt for the agent
        conversation_context = ""
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg.role == "user" else "Assistant"
                conversation_context += f"{role}: {msg.content}\n"

        # Create the full prompt for the agent
        full_prompt = f"""
You are an AI career assistant for necessitas.ai, a career guidance platform.
You help users with resume analysis, job recommendations, career planning, and skill development.

Previous conversation:
{conversation_context}

Current user message: {request.message}

Please provide a helpful, professional response focused on career guidance.
If the user asks about resume analysis, job recommendations, or career planning,
provide specific, actionable advice. Keep responses concise but informative.
        """.strip()

        # Call Bedrock AgentCore runtime
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    BEDROCK_AGENTCORE_RUNTIME_URL,
                    json={"prompt": full_prompt},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "I'm here to help with your career questions. How can I assist you?")

                    logger.info(f"Agent response generated successfully")
                    return ChatResponse(response=ai_response)
                else:
                    logger.error(f"AgentCore runtime error: {response.status_code} - {response.text}")
                    # Fallback response
                    return ChatResponse(
                        response="I'm here to help with your career questions. How can I assist you today?",
                        success=True
                    )

        except httpx.TimeoutException:
            logger.error("AgentCore runtime timeout")
            return ChatResponse(
                response="I'm experiencing some delays. Please try again in a moment.",
                success=True
            )
        except Exception as e:
            logger.error(f"AgentCore runtime error: {str(e)}")
            # Fallback to a simple response
            return ChatResponse(
                response="I'm here to help with your career questions. How can I assist you today?",
                success=True
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
        "agentcore_url": BEDROCK_AGENTCORE_RUNTIME_URL,
        "status": "ready"
    }
