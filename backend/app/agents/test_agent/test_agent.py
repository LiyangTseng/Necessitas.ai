"""
Test Agent - Multi-Agent Career Learning Path System
三個專門的 Agent 協同工作，提供完整的職涯學習路徑規劃：
- JobMarketAdvisor: 分析職場市場趨勢和機會
- LearningPathAdvisor: 設計個人化學習路徑和技能發展計畫
- CareerStrategyAdvisor: 整合建議並制定完整職涯策略
"""

import os
import sys
from typing import Dict, Any, List
from collections import defaultdict
import json

# Add backend/app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter

from tools import (
    search_jobs,
    parse_resume_text,
    analyze_skill_gap,
    match_jobs_to_profile,
    generate_learning_path,
    get_job_market_insights,
    set_current_agent
)

# Initialize BedrockAgentCore app
app = BedrockAgentCoreApp()

# Configuration
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "memory_ymkys-OsxFMnFs19")
REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = "us.amazon.nova-premier-v1:0"

# --- Code Interpreter ---
ci_sessions = {}
current_session = None


# --- Shared Memory for Multi-Agent Communication ---
class SharedMemory:
    """Shared memory system for inter-agent communication."""

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}

    def broadcast_message(self, sender: str, message: str, data: Dict[str, Any] = None):
        """Broadcast a message from one agent to all others."""
        self.messages.append({
            "sender": sender,
            "message": message,
            "data": data or {},
            "timestamp": len(self.messages)
        })

    def read_messages(self, agent_name: str, since_index: int = 0) -> List[Dict[str, Any]]:
        """Read messages from other agents."""
        return [
            msg for msg in self.messages[since_index:]
            if msg["sender"] != agent_name
        ]

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the conversation."""
        return self.messages

    def set_context(self, key: str, value: Any):
        """Set a shared context value."""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a shared context value."""
        return self.context.get(key, default)

    def clear(self):
        """Clear all messages and context."""
        self.messages = []
        self.context = {}


# Global shared memory
shared_memory = SharedMemory()

# Global tool call tracker
class ToolCallTracker:
    """Track tool calls across all agents."""

    def __init__(self):
        self.tool_calls = defaultdict(int)  # tool_name -> count
        self.agent_tool_calls = defaultdict(lambda: defaultdict(int))  # agent -> tool_name -> count
        self.call_sequence = []  # List of (agent, tool, timestamp)

    def record_call(self, agent_name: str, tool_name: str):
        """Record a tool call."""
        self.tool_calls[tool_name] += 1
        self.agent_tool_calls[agent_name][tool_name] += 1
        self.call_sequence.append({
            "agent": agent_name,
            "tool": tool_name,
            "call_number": len(self.call_sequence) + 1
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all tool calls."""
        return {
            "total_tool_calls": sum(self.tool_calls.values()),
            "tool_call_counts": dict(self.tool_calls),
            "agent_tool_calls": {
                agent: dict(tools)
                for agent, tools in self.agent_tool_calls.items()
            },
            "call_sequence": self.call_sequence
        }

    def print_summary(self):
        """Print a formatted summary of tool calls."""
        print("\n" + "="*80)
        print("🔧 TOOL CALL SUMMARY")
        print("="*80)

        # Overall statistics
        print(f"\n📊 Overall Statistics:")
        print(f"   Total tool calls: {sum(self.tool_calls.values())}")
        print(f"   Unique tools used: {len(self.tool_calls)}")

        # Tool call counts
        print(f"\n🛠️  Tool Usage:")
        for tool, count in sorted(self.tool_calls.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {tool}: {count} call(s)")

        # Per-agent breakdown
        print(f"\n🤖 Per-Agent Breakdown:")
        for agent, tools in self.agent_tool_calls.items():
            print(f"\n   {agent}:")
            for tool, count in sorted(tools.items(), key=lambda x: x[1], reverse=True):
                print(f"      └─ {tool}: {count} call(s)")

        # Call sequence
        print(f"\n📝 Call Sequence:")
        for i, call in enumerate(self.call_sequence, 1):
            print(f"   {i}. [{call['agent']}] → {call['tool']}")

        print("\n" + "="*80 + "\n")

    def clear(self):
        """Clear all tracked calls."""
        self.tool_calls.clear()
        self.agent_tool_calls.clear()
        self.call_sequence.clear()

# Global tool call tracker
tool_tracker = ToolCallTracker()


def create_agent(name: str, system_prompt: str, tools: List) -> Agent:
    """
    Create an agent with specified configuration.

    Args:
        name: Agent name/identifier
        system_prompt: System prompt defining agent behavior
        tools: List of tools available to the agent

    Returns:
        Configured Agent instance
    """
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id='default',
        actor_id=name,
        retrieval_config={}
    )

    return Agent(
        model=MODEL_ID,
        session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
        system_prompt=system_prompt,
        tools=tools
    )


# --- Agent Definitions with Enhanced System Prompts ---

JOB_MARKET_ADVISOR_PROMPT = """You are a **Job Market Advisor** specialized in analyzing job market trends and opportunities.

Your responsibilities:
1. **Market Analysis**: Search and analyze current job market conditions for specific roles and locations
2. **Opportunity Identification**: Find relevant job opportunities that match user qualifications
3. **Trend Insights**: Identify in-demand skills, growing industries, and emerging opportunities
4. **Salary & Demand**: Provide insights on compensation trends and job demand levels
5. **Geographic Analysis**: Compare opportunities across different locations and remote work options

Your expertise:
- Deep understanding of tech industry trends and hiring patterns
- Ability to identify high-growth sectors and companies
- Knowledge of competitive salary ranges and benefits
- Awareness of remote work trends and geographic variations

When analyzing jobs:
- Focus on quality over quantity - identify the best opportunities
- Highlight growth companies and innovative organizations
- Consider work-life balance, company culture, and career growth potential
- Provide specific, actionable insights backed by real market data

Communication style:
- Professional and data-driven
- Provide specific numbers and statistics when available
- Highlight key trends and opportunities clearly
- Be honest about competitive landscape and challenges

Always use your tools to gather real-time job market data before providing recommendations.
"""

LEARNING_PATH_ADVISOR_PROMPT = """You are a **Learning Path Advisor** specialized in personalized career development and skill acquisition.

IMPORTANT: The user may have provided their resume directly in the prompt. If skills are provided, they have been automatically extracted from the user's resume.

Your responsibilities:
1. **Skill Gap Analysis**: Analyze the gap between current skills and target role requirements
2. **Learning Path Design**: Create structured, timeline-based learning plans
3. **Resource Curation**: Recommend specific courses, books, and practice platforms
4. **Progress Milestones**: Define clear milestones and success criteria for each learning phase
5. **Practical Application**: Emphasize hands-on projects and real-world skill application

Your expertise:
- Deep knowledge of learning methodologies and adult education principles
- Understanding of technical skill progression and prerequisite relationships
- Familiarity with top learning platforms, courses, and certifications
- Experience with project-based learning and portfolio development
- Knowledge of industry-recognized certifications and their value

When designing learning paths:
- Start with fundamentals and build progressively
- Balance theory with hands-on practice (60% practical, 40% theory)
- Include regular milestones and checkpoints (every 2-4 weeks)
- Recommend 10-15 hours of study per week for realistic timelines
- Emphasize building a portfolio of projects demonstrating skills
- Consider different learning styles (visual, hands-on, reading)

Your learning path should include:
- Month-by-month breakdown with specific goals
- Recommended courses, books, and tutorials
- Practice projects to build portfolio
- Community resources and networking opportunities
- Certification goals where applicable
- Regular self-assessment checkpoints

Communication style:
- Encouraging and motivating
- Specific and actionable (concrete resources, not generic advice)
- Realistic about time commitments and difficulty levels
- Emphasize incremental progress and small wins

Always use your tools to analyze skill gaps and generate detailed learning paths before advising.
"""

CAREER_STRATEGY_ADVISOR_PROMPT = """You are a **Career Strategy Advisor** who integrates market insights and learning plans into comprehensive career strategies.

Your responsibilities:
1. **Strategic Integration**: Synthesize insights from Job Market Advisor and Learning Path Advisor
2. **Career Roadmap**: Create holistic 6-12 month career transition plans
3. **Priority Setting**: Help prioritize actions based on impact and feasibility
4. **Risk Assessment**: Identify potential challenges and mitigation strategies
5. **Action Planning**: Convert strategy into specific, weekly action items
6. **Motivation & Accountability**: Provide encouragement and realistic expectations

Your expertise:
- Strategic career planning and transition management
- Understanding of hiring processes and what companies look for
- Knowledge of networking strategies and personal branding
- Experience with resume optimization and interview preparation
- Awareness of career pivots and upskilling success stories

When creating career strategies:
- **Phase 1 (Month 1-2)**: Foundation building and quick wins
  - Start with most in-demand skills
  - Build initial projects for portfolio
  - Update resume and LinkedIn profile
  - Begin networking in target industry

- **Phase 2 (Month 3-4)**: Deep skill development
  - Focus on advanced skills and specialization
  - Complete 2-3 substantial portfolio projects
  - Earn relevant certifications
  - Engage with technical communities

- **Phase 3 (Month 5-6)**: Job search preparation
  - Polish portfolio and online presence
  - Practice technical interviews
  - Start applying to positions (10-15 applications)
  - Leverage network for referrals

Your strategy should address:
- **Short-term goals** (1-2 months): Quick wins and foundation
- **Medium-term goals** (3-4 months): Deep skill development
- **Long-term goals** (5-6 months): Job search and transition
- **Networking strategy**: LinkedIn, meetups, conferences, communities
- **Financial planning**: Costs of courses, time commitment, transition timeline
- **Backup plans**: Alternative roles, freelance opportunities, parallel paths

Integration guidelines:
- Review and synthesize ALL messages from other agents
- Identify conflicts or gaps in their recommendations
- Create a unified, coherent strategy
- Prioritize actions by impact and effort
- Set clear success metrics and checkpoints
- Provide weekly action items for the first month

Communication style:
- Strategic and comprehensive
- Balanced between ambition and realism
- Empowering and confidence-building
- Specific action-oriented guidance
- Address concerns and potential obstacles proactively

Always read messages from other agents before formulating your strategy. Your role is to synthesize their insights into an actionable career plan.
"""


# Create the three specialized agents
agents = {
    "JobMarketAdvisor": create_agent(
        "JobMarketAdvisor",
        JOB_MARKET_ADVISOR_PROMPT,
        [search_jobs, get_job_market_insights, match_jobs_to_profile]
    ),
    "LearningPathAdvisor": create_agent(
        "LearningPathAdvisor",
        LEARNING_PATH_ADVISOR_PROMPT,
        [analyze_skill_gap, generate_learning_path, parse_resume_text]
    ),
    "CareerStrategyAdvisor": create_agent(
        "CareerStrategyAdvisor",
        CAREER_STRATEGY_ADVISOR_PROMPT,
        [analyze_skill_gap, generate_learning_path, search_jobs, get_job_market_insights]
    )
}


def detect_and_parse_resume(user_prompt: str) -> tuple[str, List[str], str]:
    """
    Detect if prompt contains resume content and parse it.

    Args:
        user_prompt: User's prompt that may contain resume

    Returns:
        Tuple of (cleaned_prompt, extracted_skills, detected_target_role)
    """
    # Simple heuristics to detect resume content
    resume_indicators = [
        'experience:', 'education:', 'skills:', 'resume:',
        'curriculum vitae', 'cv:', 'work history',
        'bachelor', 'master', 'university', 'degree',
        'years of experience', 'worked at', 'software engineer'
    ]

    prompt_lower = user_prompt.lower()
    has_resume = any(indicator in prompt_lower for indicator in resume_indicators)

    if has_resume and len(user_prompt) > 200:  # Likely contains resume
        print("\n📄 Detected resume content in prompt. Parsing...")

        # Parse the resume
        from tools import parse_resume_text
        parsed_result = parse_resume_text(user_prompt)

        if parsed_result.get("success"):
            data = parsed_result["data"]
            skills = data.get("skills", [])

            # Try to detect target role from the prompt
            target_role = None
            role_keywords = {
                "data scientist": ["data scientist", "data science"],
                "software engineer": ["software engineer", "swe", "software developer"],
                "full stack": ["full stack", "fullstack"],
                "frontend": ["frontend", "front-end", "front end"],
                "backend": ["backend", "back-end", "back end"],
                "devops": ["devops", "dev ops"],
                "machine learning": ["machine learning", "ml engineer"],
            }

            for role, keywords in role_keywords.items():
                if any(keyword in prompt_lower for keyword in keywords):
                    target_role = role.title()
                    break

            # Extract the actual question/request from prompt
            # Usually after resume content, there's a question
            question_indicators = ["help me", "i want", "i need", "suggest", "recommend",
                                 "what should", "how can", "please", "guide me", "advice"]

            cleaned_prompt = user_prompt
            for indicator in question_indicators:
                if indicator in prompt_lower:
                    # Extract the question part
                    idx = prompt_lower.index(indicator)
                    question_part = user_prompt[idx:]
                    if len(question_part) < len(user_prompt) * 0.3:  # Question is < 30% of prompt
                        cleaned_prompt = question_part
                    break

            print(f"✓ Parsed resume: {len(skills)} skills extracted")
            if target_role:
                print(f"✓ Detected target role: {target_role}")

            return cleaned_prompt, skills, target_role

    return user_prompt, [], None


def orchestrate_multi_agent_conversation(user_prompt: str, user_skills: List[str] = None, target_role: str = None) -> Dict[str, Any]:
    """
    Orchestrate a multi-agent conversation to provide comprehensive career guidance.

    Args:
        user_prompt: User's initial question or request (may contain resume content)
        user_skills: Optional list of user's current skills
        target_role: Optional target job role

    Returns:
        Dictionary containing all agent responses and final recommendations
    """
    # Auto-detect and parse resume if present in prompt
    if not user_skills or len(user_skills) == 0:
        cleaned_prompt, auto_skills, auto_target = detect_and_parse_resume(user_prompt)
        if auto_skills:
            user_prompt = cleaned_prompt
            user_skills = auto_skills
            if auto_target and not target_role:
                target_role = auto_target

    # Clear previous conversation and tool tracker
    shared_memory.clear()
    tool_tracker.clear()

    print("\n" + "="*80)
    print("🚀 STARTING MULTI-AGENT CONVERSATION")
    print("="*80)

    # Store user context
    shared_memory.set_context("user_skills", user_skills or [])
    shared_memory.set_context("target_role", target_role)
    shared_memory.set_context("user_prompt", user_prompt)
    shared_memory.set_context("resume_parsed", bool(user_skills))

    responses = {}

    # Step 1: Job Market Advisor analyzes the market
    print("\n" + "="*80)
    print("📊 STEP 1: JobMarketAdvisor Analyzing Job Market")
    print("="*80)

    set_current_agent("JobMarketAdvisor")

    resume_context = ""
    if shared_memory.get_context("resume_parsed"):
        resume_context = "\n**Note**: User's skills were automatically extracted from their resume.\n"

    job_market_prompt = f"""
User's request: {user_prompt}
User's skills: {user_skills or 'Not provided'}{resume_context}
Target role: {target_role or 'To be determined'}

Please analyze the job market for this scenario:
1. Search for relevant job opportunities
2. Analyze market demand and trends
3. Identify top required skills in the market
4. Provide salary insights and growth trends
5. Recommend best opportunities based on the user's profile

Use your tools to gather real market data.
"""

    job_market_response = agents["JobMarketAdvisor"](job_market_prompt)
    job_market_text = job_market_response.message.get('content', [{}])[0].get('text', str(job_market_response))

    responses["JobMarketAdvisor"] = job_market_text
    shared_memory.broadcast_message(
        "JobMarketAdvisor",
        job_market_text,
        {"role": "market_analysis"}
    )

    # Step 2: Learning Path Advisor creates learning plan
    print("\n" + "="*80)
    print("📚 STEP 2: LearningPathAdvisor Creating Learning Plan")
    print("="*80)

    set_current_agent("LearningPathAdvisor")

    other_messages = shared_memory.read_messages("LearningPathAdvisor")
    context_info = "\n".join([f"- {msg['sender']}: {msg['message'][:500]}..." for msg in other_messages])

    learning_path_prompt = f"""
User's request: {user_prompt}
User's skills: {user_skills or 'Not provided'}{resume_context}
Target role: {target_role or 'To be determined'}

Context from other agents:
{context_info}

Based on the job market analysis, please:
1. Analyze the skill gap between user's current skills and market requirements
2. Generate a detailed 6-month learning path
3. Provide specific courses, resources, and project recommendations
4. Define clear milestones and success criteria
5. Estimate time commitment and difficulty level

Use your tools to create a data-driven learning plan.
"""

    learning_path_response = agents["LearningPathAdvisor"](learning_path_prompt)
    learning_path_text = learning_path_response.message.get('content', [{}])[0].get('text', str(learning_path_response))

    responses["LearningPathAdvisor"] = learning_path_text
    shared_memory.broadcast_message(
        "LearningPathAdvisor",
        learning_path_text,
        {"role": "learning_path"}
    )

    # Step 3: Career Strategy Advisor synthesizes everything
    print("\n" + "="*80)
    print("🎯 STEP 3: CareerStrategyAdvisor Creating Integrated Strategy")
    print("="*80)

    set_current_agent("CareerStrategyAdvisor")

    all_messages = shared_memory.get_all_messages()
    full_context = "\n\n".join([
        f"**{msg['sender']}** said:\n{msg['message']}"
        for msg in all_messages
    ])

    career_strategy_prompt = f"""
User's request: {user_prompt}
User's skills: {user_skills or 'Not provided'}{resume_context}
Target role: {target_role or 'To be determined'}

**Complete context from other advisors:**
{full_context}

As the Career Strategy Advisor, your job is to:
1. Review and synthesize ALL insights from JobMarketAdvisor and LearningPathAdvisor
2. Create a comprehensive 6-month career transition strategy
3. Prioritize actions into short-term (1-2 months), medium-term (3-4 months), and long-term (5-6 months) goals
4. Provide specific weekly action items for the first month
5. Address potential challenges and provide mitigation strategies
6. Set clear success metrics and checkpoints

Create an actionable, integrated career strategy that combines market insights with the learning plan.
"""

    career_strategy_response = agents["CareerStrategyAdvisor"](career_strategy_prompt)
    career_strategy_text = career_strategy_response.message.get('content', [{}])[0].get('text', str(career_strategy_response))

    responses["CareerStrategyAdvisor"] = career_strategy_text
    shared_memory.broadcast_message(
        "CareerStrategyAdvisor",
        career_strategy_text,
        {"role": "final_strategy"}
    )

    # Print tool call summary
    tool_tracker.print_summary()

    # Print conversation flow summary
    print("="*80)
    print("💬 CONVERSATION FLOW SUMMARY")
    print("="*80)
    for i, msg in enumerate(shared_memory.get_all_messages(), 1):
        print(f"\n{i}. {msg['sender']}:")
        preview = msg['message'][:200] + "..." if len(msg['message']) > 200 else msg['message']
        print(f"   {preview}")
    print("\n" + "="*80)

    # Get tool call summary for response
    tool_summary = tool_tracker.get_summary()

    return {
        "success": True,
        "user_prompt": user_prompt,
        "user_skills": user_skills,
        "target_role": target_role,
        "agent_responses": responses,
        "conversation_flow": shared_memory.get_all_messages(),
        "final_strategy": career_strategy_text,
        "tool_call_summary": tool_summary  # Add tool call summary to response
    }


# --- Entrypoint ---
@app.entrypoint
def invoke(payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entrypoint for the test agent.

    Payload format:
    {
        "prompt": "User's question or request",
        "user_skills": ["Python", "JavaScript"],  # Optional
        "target_role": "Data Scientist",  # Optional
        "mode": "conversation"  # or "single_agent"
    }
    """
    global current_session

    if not MEMORY_ID:
        return {"error": "Memory not configured. Set BEDROCK_AGENTCORE_MEMORY_ID environment variable."}

    # Extract parameters
    user_prompt = payload.get("prompt", "")
    user_skills = payload.get("user_skills", [])
    target_role = payload.get("target_role", None)
    mode = payload.get("mode", "conversation")  # conversation or single_agent

    # Set current session
    current_session = getattr(context, 'session_id', 'default')

    if mode == "conversation":
        # Multi-agent orchestrated conversation
        result = orchestrate_multi_agent_conversation(user_prompt, user_skills, target_role)
        return result
    else:
        # Single agent mode (backward compatibility)
        actor_id = context.headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'CareerStrategyAdvisor') if hasattr(context, 'headers') else 'CareerStrategyAdvisor'
        agent = agents.get(actor_id, agents["CareerStrategyAdvisor"])

        # Read messages from other agents
        other_msgs = shared_memory.read_messages(actor_id)
        context_prompt = ""
        if other_msgs:
            context_prompt = "Other agents said:\n"
            for m in other_msgs:
                context_prompt += f"- {m['sender']}: {m['message'][:200]}...\n"

        final_prompt = f"{context_prompt}\nUser asked: {user_prompt}"

        # Generate response
        result = agent(final_prompt)
        response_text = result.message.get('content', [{}])[0].get('text', str(result))

        # Broadcast to shared memory
        shared_memory.broadcast_message(actor_id, response_text)

        return {"response": response_text, "agent": actor_id}


if __name__ == "__main__":
    app.run()
