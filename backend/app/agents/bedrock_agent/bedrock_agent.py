"""
Multi-Agent Bedrock AgentCore Sample
Three agents communicate via shared memory:
- JobAdvisor: 提供職缺建議
- LearningPathAdvisor: 提供學習路徑
- SummaryAdvisor: 統整資訊並提供最終職涯報告
"""

import os
import logging
from strands import Agent, tool
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# === 初始化應用 ===
app = BedrockAgentCoreApp()
logging.basicConfig(level=logging.INFO)

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION")
MODEL_ID = "us.amazon.nova-premier-v1:0"

# --- Code Interpreter 工具 ---
ci_sessions = {}
current_session = None

# --- 共用記憶體 ---
shared_memory = {"messages": []}

@tool
def broadcast_message(sender, message):
    shared_memory["messages"].append({"sender": sender, "text": message})
    logging.info(f"[Broadcast] {sender} → shared memory")

@tool
def read_messages(agent_name):
    return [m for m in shared_memory.get("messages", []) if m["sender"] != agent_name]

# --- 建立 Agent ---
def create_agent(name, system_prompt):
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
        tools=[broadcast_message, read_messages]
    )

agents = {
    "JobAdvisor": create_agent(
        "JobAdvisor",
        "You are a career expert who provides detailed and realistic job suggestions based on a resume, skills, and goals."
    ),
    "LearningPathAdvisor": create_agent(
        "LearningPathAdvisor",
        "You are a learning path advisor who designs concrete study plans, online courses, and skill development strategies."
    ),
    "SummaryAdvisor": create_agent(
        "SummaryAdvisor",
        "You are a professional report writer who combines job and learning advice into a 2000-word career development report."
    )
}

# --- 主控制流程 ---
@app.entrypoint
def invoke(payload, context):
    global current_session

    if not MEMORY_ID:
        return {"error": "Memory not configured"}

    current_session = getattr(context, 'session_id', 'default')
    user_prompt = payload.get("prompt", "")
    logging.info("=== Multi-Agent Career Planner Started ===")

    # Step 1: JobAdvisor 處理履歷並提出職缺建議
    job_agent = agents["JobAdvisor"]
    job_prompt = f"""You are a senior career advisor AI. Your task is to identify current job openings at top 30 companies worldwide that align with the user's profile. For each job recommendation, provide:
                    Job Details: title, company, location, responsibilities, required skills, and seniority level.
                    Fit Analysis: explain why this job suits the user's skills, experience, and career goals.
                    Actionable Improvement Suggestions: if there are skill or experience gaps, provide clear steps the user can take to become a stronger candidate.
                    Optional Growth Insights: suggest potential career growth paths or related roles for long-term development.
                    User resume or profile:
                    {user_prompt}
                    Instruction: Provide comprehensive, specific, and actionable job recommendations based on the user's profile."""
    job_result = job_agent(job_prompt)
    job_text = job_result.message.get('content', [{}])[0].get('text', str(job_result))
    broadcast_message("JobAdvisor", job_text)
    logging.info("[JobAdvisor] Finished")

    # Step 2: LearningPathAdvisor 依據職缺建議給出學習方向
    learning_agent = agents["LearningPathAdvisor"]
    learning_prompt = (
        f"""You are a professional learning path advisor AI. Your task is to design a 6-month learning plan for the user based on the job recommendations provided. For each job, consider the required skills, experience gaps, and career goals.
            Your response must include:
            Monthly Plan: Break down the 6 months into clear, actionable steps.
            Skill Focus: Specify which skills or knowledge areas to acquire or strengthen each month.
            Practical Actions: Include exercises, projects, or resources that will help the user gain the required skills.
            Progress Metrics: Suggest ways to measure improvement or readiness for the target jobs.
            Job Recommendations:
            {job_text}
            Instruction: Provide a structured, practical, and actionable 6-month learning plan tailored to the user’s profile and the given job recommendations."""
    )
    learning_result = learning_agent(learning_prompt)
    learning_text = learning_result.message.get('content', [{}])[0].get('text', str(learning_result))
    broadcast_message("LearningPathAdvisor", learning_text)
    logging.info("[LearningPathAdvisor] Finished")

    # Step 3: SummaryAdvisor 統整並產出完整報告
    summary_agent = agents["SummaryAdvisor"]
    summary_prompt = (
        f"""You are a senior career report advisor AI. Your task is to combine the outputs from JobAdvisor and LearningPathAdvisor into a single, cohesive, structured report of approximately 2000 words.
            Your report must include:
            Introduction: Summarize the user's profile, career goals, and the context of the analysis.
            Job Fit Analysis: Present and analyze recommended jobs, highlighting alignment with the user's skills and experience.
            Skill Roadmap: Integrate the 6-month learning plan, showing how it addresses skill gaps for the recommended jobs.
            Final Recommendations: Provide actionable advice for next steps, long-term career development, and potential growth paths.
            Inputs:
            JobAdvisor output: {job_text}
            LearningPathAdvisor output: {learning_text}
            Instruction: Produce a structured, coherent, and professional career report suitable for a senior-level review. Ensure clarity, logical flow, and actionable insights throughout."""
    )
    summary_result = summary_agent(summary_prompt)
    summary_text = summary_result.message.get('content', [{}])[0].get('text', str(summary_result))
    broadcast_message("SummaryAdvisor", summary_text)
    logging.info("[SummaryAdvisor] Finished and report generated")

    # --- 最終輸出 ---
    logging.info("=== All Agents Finished ===")
    return {
        "job_recommendations": job_text,
        "learning_path": learning_text,
        "final_report": summary_text 
    }

if __name__ == "__main__":
    app.run()
