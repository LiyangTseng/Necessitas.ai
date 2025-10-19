"""
Multi-Agent Bedrock AgentCore Sample
Three agents communicate via shared memory:
- JobAdvisor: 提供職缺建議
- LearningPathAdvisor: 提供學習路徑
- SummaryAdvisor: 統整資訊並提供建議
"""
import os
from strands import Agent, tool
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from tools import find_job_matches, parse_resume, search_jobs, get_company_info, analyze_skill_gap, generate_career_roadmap

app = BedrockAgentCoreApp()

# TODO: get from config
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "memory_ymkys-OsxFMnFs19")
REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = "us.amazon.nova-premier-v1:0"

# --- Code Interpreter ---
ci_sessions = {}
current_session = None

@tool
def calculate(code: str) -> str:
    session_id = current_session or 'default'
    if session_id not in ci_sessions:
        ci_sessions[session_id] = {'client': CodeInterpreter(REGION), 'session_id': None}
    ci = ci_sessions[session_id]
    if not ci['session_id']:
        ci['session_id'] = ci['client'].start(name=f"session_{session_id[:30]}", session_timeout_seconds=1800)
    result = ci['client'].invoke("executeCode", {"code": code, "language": "python"})
    for event in result.get("stream", []):
        if stdout := event.get("result", {}).get("structuredContent", {}).get("stdout"):
            return stdout
    return "Executed"

# --- Shared Memory for Multi-Agent Communication ---
shared_memory = {"messages": []}

def broadcast_message(sender, message):
    shared_memory["messages"].append({"sender": sender, "text": message})

def read_messages(agent_name):
    return [m for m in shared_memory.get("messages", []) if m["sender"] != agent_name]

# --- Agent Initialization ---
def create_agent(name, system_prompt, tools):
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

agents = {
    "JobAdvisor": create_agent(
        "JobAdvisor",
        "You are a career expert who provides job suggestions based on user resume and goals.",
        [search_jobs]
    ),
    "LearningPathAdvisor": create_agent(
        "LearningPathAdvisor",
        "You are a learning path advisor who gives study/training suggestions.",
        [parse_resume, analyze_skill_gap, generate_career_roadmap, get_company_info]
    ),
    "SummaryAdvisor": create_agent(
        "SummaryAdvisor",
        "You are a summarizer who consolidates advice from other agents and gives a career plan.",
        [find_job_matches, parse_resume, search_jobs, get_company_info, analyze_skill_gap, generate_career_roadmap]
    ),
}

# --- Entrypoint ---
@app.entrypoint
def invoke(payload, context):
    global current_session

    if not MEMORY_ID:
        return {"error": "Memory not configured"}

    actor_id = context.headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'JobAdvisor') if hasattr(context, 'headers') else 'JobAdvisor'
    current_session = getattr(context, 'session_id', 'default')

    # 選取對應 Agent
    agent = agents.get(actor_id, agents["JobAdvisor"])

    # 讀取其他 Agent 訊息
    other_msgs = read_messages(actor_id)
    context_prompt = ""
    if other_msgs:
        context_prompt = "Other agents said:\n"
        for m in other_msgs:
            context_prompt += f"- {m['sender']}: {m['text']}\n"

    user_prompt = payload.get("prompt", "")
    final_prompt = f"{context_prompt}\nUser asked: {user_prompt}"

    # Agent 產生回應
    result = agent(final_prompt)
    response_text = result.message.get('content', [{}])[0].get('text', str(result))

    # 廣播回應到共享記憶
    broadcast_message(actor_id, response_text)

    return {"response": response_text}


if __name__ == "__main__":
    app.run()
