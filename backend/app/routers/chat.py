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
from core.session import SessionManager

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

        # Build enhanced prompt with resume context
        enhanced_prompt = request.message

        # Add resume context if available
        if request.session_id:
            resume_data = SessionManager.get_resume_data(request.session_id)
            if resume_data:
                resume_context = f"""
Resume Context:
- Name: {resume_data.personal_info.full_name if resume_data.personal_info else 'Not provided'}
- Skills: {', '.join(resume_data.skills[:10]) if resume_data.skills else 'None listed'}
- Experience: {len(resume_data.experience)} positions
- Education: {len(resume_data.education)} entries
- Summary: {resume_data.summary[:200] if resume_data.summary else 'No summary available'}

User Question: {request.message}
"""
                enhanced_prompt = resume_context
                logger.info(f"Enhanced prompt with resume context for session: {request.session_id}")

        # Get raw response from agent
        raw_response = invoke_agent(
            prompt=enhanced_prompt,
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

@router.post("/chat/session")
async def create_chat_session():
    """Create a new chat session."""
    session_id = SessionManager.create_session()
    return {"session_id": session_id}

@router.post("/chat/session/{session_id}/resume")
async def store_resume_in_session(session_id: str, resume_data: dict):
    """Store parsed resume data in a chat session."""
    try:
        # Convert dict to ResumeData object
        from models.user import ResumeData, PersonalInfo, Experience, Education, Certification
        from datetime import datetime

        # This is a simplified conversion - you might want to add validation
        resume_obj = ResumeData(
            personal_info=PersonalInfo(**resume_data.get("personal_info", {})),
            summary=resume_data.get("summary", ""),
            skills=resume_data.get("skills", []),
            experience=[Experience(**exp) for exp in resume_data.get("experience", [])],
            education=[Education(**edu) for edu in resume_data.get("education", [])],
            certifications=[Certification(**cert) for cert in resume_data.get("certifications", [])],
            raw_text=resume_data.get("raw_text", ""),
            confidence_score=resume_data.get("confidence_score", 0.0)
        )

        success = SessionManager.update_resume_data(session_id, resume_obj)

        if success:
            return {"message": "Resume data stored successfully", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        logger.error(f"Failed to store resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store resume data: {str(e)}")
