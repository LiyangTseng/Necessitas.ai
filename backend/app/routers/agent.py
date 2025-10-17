from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.bedrock_agent.bedrock_agent import app

router = APIRouter()

class AgentRequest(BaseModel):
    prompt: str
    agent_type: str = "CareerAdvisor"  # ResumeAnalyzer, JobMatcher, CareerAdvisor
    user_data: dict = None

@router.post("/chat")
async def chat_with_agent(request: AgentRequest):
    # Call Bedrock AgentCore
    result = app.invoke(
        request.prompt,
        context={
            "agent_type": request.agent_type,
            "user_data": request.user_data,
        }
    )
    return result
