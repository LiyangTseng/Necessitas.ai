"""
AI Agent Router

Handles interactions with the Bedrock AI agent for career guidance.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.agents.bedrock_agent.bedrock_agent import BedrockAgent

router = APIRouter()


@router.post("/chat")
async def chat_with_agent(
    message: str, user_id: str, session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with the AI career guidance agent.

    Args:
        message: User message
        user_id: User ID
        session_id: Optional session ID for conversation continuity

    Returns:
        Agent response and recommendations
    """
    try:
        # Initialize Bedrock agent
        agent = BedrockAgent()

        # Process message
        response = await agent.process_message(
            message=message, user_id=user_id, session_id=session_id
        )

        return {
            "user_id": user_id,
            "session_id": response.get("session_id"),
            "message": message,
            "response": response.get("response"),
            "recommendations": response.get("recommendations", []),
            "action_items": response.get("action_items", []),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent chat failed: {str(e)}")


@router.get("/career-guidance/{user_id}")
async def get_career_guidance(
    user_id: str,
    question: str = Query(..., description="Career question"),
    context: Optional[str] = Query(None, description="Additional context"),
) -> Dict[str, Any]:
    """
    Get personalized career guidance from the AI agent.

    Args:
        user_id: User ID
        question: Career question
        context: Optional additional context

    Returns:
        Personalized career guidance
    """
    try:
        # Initialize Bedrock agent
        agent = BedrockAgent()

        # Get career guidance
        guidance = await agent.get_career_guidance(
            user_id=user_id, question=question, context=context
        )

        return {
            "user_id": user_id,
            "question": question,
            "context": context,
            "guidance": guidance,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career guidance failed: {str(e)}")


@router.post("/analyze-profile")
async def analyze_user_profile(
    user_id: str, profile_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze user profile and provide AI-powered insights.

    Args:
        user_id: User ID
        profile_data: User profile data

    Returns:
        AI analysis and insights
    """
    try:
        # Initialize Bedrock agent
        agent = BedrockAgent()

        # Analyze profile
        analysis = await agent.analyze_profile(
            user_id=user_id, profile_data=profile_data
        )

        return {
            "user_id": user_id,
            "analysis": analysis,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Profile analysis failed: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session_history(session_id: str) -> Dict[str, Any]:
    """
    Get conversation history for a session.

    Args:
        session_id: Session ID

    Returns:
        Conversation history
    """
    try:
        # This would typically fetch from database
        # For now, return mock data
        return {
            "session_id": session_id,
            "conversation_history": [
                {
                    "timestamp": "2024-01-15T10:00:00Z",
                    "user_message": "What skills should I learn for a software engineering role?",
                    "agent_response": "Based on your profile, I recommend focusing on Python, AWS, and Machine Learning. These skills are in high demand and align with your background.",
                    "recommendations": [
                        "Take an AWS certification course",
                        "Build a machine learning project",
                        "Practice Python coding challenges",
                    ],
                },
                {
                    "timestamp": "2024-01-15T10:05:00Z",
                    "user_message": "What's the salary range for Python developers?",
                    "agent_response": "Python developers typically earn $70,000 - $130,000 depending on experience and location. Senior developers can earn $120,000+.",
                    "recommendations": [
                        "Research salary data for your specific location",
                        "Consider remote work opportunities",
                        "Focus on high-demand Python frameworks",
                    ],
                },
            ],
            "session_created": "2024-01-15T10:00:00Z",
            "last_activity": "2024-01-15T10:05:00Z",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get session history: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> Dict[str, Any]:
    """
    Clear conversation history for a session.

    Args:
        session_id: Session ID

    Returns:
        Confirmation of session clearing
    """
    try:
        # This would typically clear from database
        return {
            "session_id": session_id,
            "status": "cleared",
            "message": "Session history cleared successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear session: {str(e)}"
        )
