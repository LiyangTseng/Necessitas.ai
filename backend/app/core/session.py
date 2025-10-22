"""
Session Management

Simple in-memory session storage for user data.
In production, this should be replaced with Redis or database storage.
"""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
from models.user import ResumeData

# In-memory session storage (replace with Redis in production)
_sessions: Dict[str, Dict[str, Any]] = {}

class SessionManager:
    """Simple session manager for storing user data."""

    @staticmethod
    def create_session() -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "created_at": datetime.now(),
            "resume_data": None,
            "conversation_history": []
        }
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        return _sessions.get(session_id)

    @staticmethod
    def update_resume_data(session_id: str, resume_data: ResumeData) -> bool:
        """Update resume data for a session."""
        if session_id in _sessions:
            _sessions[session_id]["resume_data"] = resume_data
            return True
        return False

    @staticmethod
    def get_resume_data(session_id: str) -> Optional[ResumeData]:
        """Get resume data for a session."""
        session = _sessions.get(session_id)
        return session.get("resume_data") if session else None

    @staticmethod
    def add_message(session_id: str, role: str, content: str) -> bool:
        """Add a message to conversation history."""
        if session_id in _sessions:
            if "conversation_history" not in _sessions[session_id]:
                _sessions[session_id]["conversation_history"] = []

            _sessions[session_id]["conversation_history"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False

    @staticmethod
    def get_conversation_history(session_id: str) -> list:
        """Get conversation history for a session."""
        session = _sessions.get(session_id)
        return session.get("conversation_history", []) if session else []

    @staticmethod
    def cleanup_expired_sessions(max_age_hours: int = 24):
        """Clean up expired sessions."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = [
            sid for sid, data in _sessions.items()
            if data["created_at"] < cutoff
        ]
        for sid in expired_sessions:
            del _sessions[sid]
        return len(expired_sessions)
