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
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Current working directory: %s", os.getcwd())
logger.info("Files in the current directory: %s", os.listdir(os.getcwd()))

# check if the current directory is in docker
if os.getcwd() == "/app":
    # set python path to backend/app
    os.environ["PYTHONPATH"] = "/app/backend/app"
logger.info("PYTHONPATH: %s", os.getenv("PYTHONPATH"))

try:
    from .tools import find_job_matches, parse_resume, search_jobs
    logger.info("Successfully imported tools using relative import")
except ImportError as e:
    logger.error("Relative import failed: %s", e)
    # Fallback for deployed environment
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    sys.path.append(current_dir)
    try:
        from tools import find_job_matches, parse_resume, search_jobs
        logger.info("Successfully imported tools using absolute import")
    except ImportError as e2:
        logger.error("Absolute import also failed: %s", e2)
        raise


app = BedrockAgentCoreApp()

# TODO: get from config
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "memory_ymkys-OsxFMnFs19")
REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = "us.amazon.nova-premier-v1:0"

# --- Code Interpreter ---
ci_sessions = {}
current_session = None

@tool
def dummy(code: str) -> str:
    return "dummy response"

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
        """
        You are a career advisor.
        When asked to find or list real job openings, always use the `search_jobs` tool
        instead of generating text on your own.
        Only summarize or explain after you get tool results.
        """,
        [dummy, search_jobs]
    )
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
