"""
AWS Bedrock Agent

Main agent orchestrator using AWS Bedrock AgentCore for career guidance.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import boto3
from loguru import logger

from app.core.config import settings


class BedrockAgent:
    """Main Bedrock agent for career guidance and recommendations."""

    def __init__(self):
        """Initialize the Bedrock agent."""
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self.model_id = settings.bedrock_model_id
        self.agent_id = settings.bedrock_agent_id

    async def process_message(
        self, message: str, user_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response using Bedrock.

        Args:
            message: User message
            user_id: User ID
            session_id: Optional session ID

        Returns:
            Agent response with recommendations
        """
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            # Prepare context for the agent
            context = await self._prepare_context(user_id, message)

            # Generate response using Bedrock
            response = await self._generate_response(message, context, session_id)

            # Extract recommendations and action items
            recommendations = self._extract_recommendations(response)
            action_items = self._extract_action_items(response)

            return {
                "session_id": session_id,
                "response": response,
                "recommendations": recommendations,
                "action_items": action_items,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            raise

    async def get_career_guidance(
        self, user_id: str, question: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized career guidance.

        Args:
            user_id: User ID
            question: Career question
            context: Optional additional context

        Returns:
            Career guidance response
        """
        try:
            # Prepare user profile context
            user_context = await self._get_user_context(user_id)

            # Construct prompt for career guidance
            prompt = self._construct_career_guidance_prompt(
                question, user_context, context
            )

            # Generate response
            response = await self._generate_response(prompt, user_context)

            return {
                "question": question,
                "guidance": response,
                "context": user_context,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get career guidance: {str(e)}")
            raise

    async def analyze_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user profile and provide AI-powered insights.

        Args:
            user_id: User ID
            profile_data: User profile data

        Returns:
            Profile analysis results
        """
        try:
            # Construct analysis prompt
            prompt = self._construct_profile_analysis_prompt(profile_data)

            # Generate analysis
            analysis = await self._generate_response(prompt, profile_data)

            # Parse analysis results
            parsed_analysis = self._parse_profile_analysis(analysis)

            return {
                "user_id": user_id,
                "analysis": parsed_analysis,
                "raw_analysis": analysis,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to analyze profile: {str(e)}")
            raise

    async def _prepare_context(self, user_id: str, message: str) -> Dict[str, Any]:
        """Prepare context for the agent."""
        # This would typically fetch user data from database
        # For now, return mock context
        return {
            "user_id": user_id,
            "profile": {
                "skills": ["Python", "React", "AWS", "Machine Learning"],
                "experience": "3 years",
                "target_role": "Senior Software Engineer",
                "location": "San Francisco, CA",
            },
            "conversation_history": [],
            "current_message": message,
        }

    async def _generate_response(
        self, prompt: str, context: Dict[str, Any], session_id: Optional[str] = None
    ) -> str:
        """Generate response using Bedrock."""
        try:
            # Prepare the request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"]

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            # Return fallback response
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."

    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from agent response."""
        recommendations = []

        # Look for recommendation patterns
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("• ") or line.startswith("* "):
                recommendations.append(line[2:].strip())
            elif (
                line.startswith("1. ")
                or line.startswith("2. ")
                or line.startswith("3. ")
            ):
                recommendations.append(line[3:].strip())

        return recommendations

    def _extract_action_items(self, response: str) -> List[str]:
        """Extract action items from agent response."""
        action_items = []

        # Look for action item patterns
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if "action" in line.lower() or "next step" in line.lower():
                action_items.append(line)

        return action_items

    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from database."""
        # This would typically fetch from database
        # For now, return mock data
        return {
            "user_id": user_id,
            "skills": ["Python", "React", "AWS", "Machine Learning"],
            "experience": "3 years",
            "target_role": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "preferences": {
                "remote_work": True,
                "salary_range": "$120,000 - $150,000",
                "company_size": "startup",
            },
        }

    def _construct_career_guidance_prompt(
        self,
        question: str,
        user_context: Dict[str, Any],
        additional_context: Optional[str] = None,
    ) -> str:
        """Construct prompt for career guidance."""
        prompt = f"""
You are CareerCompassAI, an intelligent career guidance assistant. Help the user with their career question.

User Profile:
- Skills: {', '.join(user_context.get('skills', []))}
- Experience: {user_context.get('experience', 'Unknown')}
- Target Role: {user_context.get('target_role', 'Not specified')}
- Location: {user_context.get('location', 'Not specified')}

User Question: {question}

{additional_context if additional_context else ''}

Please provide:
1. Direct answer to their question
2. 3-5 specific recommendations
3. Next steps they should take
4. Relevant resources or tools

Be specific, actionable, and encouraging.
"""
        return prompt

    def _construct_profile_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Construct prompt for profile analysis."""
        prompt = f"""
Analyze this user profile and provide career insights:

Profile Data:
{json.dumps(profile_data, indent=2)}

Please provide:
1. Strengths and competitive advantages
2. Areas for improvement
3. Career opportunities
4. Skill gap analysis
5. Recommended next steps

Be specific and actionable in your analysis.
"""
        return prompt

    def _parse_profile_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse profile analysis into structured format."""
        # This would typically use more sophisticated parsing
        # For now, return basic structure
        return {
            "strengths": ["Strong technical skills", "Relevant experience"],
            "improvements": ["Leadership skills", "Advanced certifications"],
            "opportunities": ["Senior roles", "Management positions"],
            "skill_gaps": ["Kubernetes", "System Design"],
            "recommendations": [
                "Pursue AWS certification",
                "Build leadership experience",
                "Learn containerization technologies",
            ],
        }
