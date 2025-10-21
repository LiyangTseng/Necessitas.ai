# necessitas.ai: Intelligent Career Path Recommendation Agent
[![CI/CD Pipeline](https://github.com/LiyangTseng/necessitas.ai/actions/workflows/ci.yml/badge.svg)](https://github.com/LiyangTseng/necessitas.ai/actions/workflows/ci.yml)

An AI-powered career guidance system that analyzes resumes, matches job opportunities, and provides personalized career roadmaps using AWS Bedrock AgentCore.

## 🚀 **Quick Start**

### Prerequisites
- Python > 3.11
- AWS CLI
- Node.js >= v18.17.0
### **Setup (One-time)**
#### Clone repo
```bash
# Clone and setup
git clone [<repository-url>](https://github.com/LiyangTseng/necessitas.ai)
cd necessitas.ai
```
Set up environment dependency
```bash
python3.11 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
# Install pre-commit hooks
pre-commit install
```

## 🎯 **Hackathon Project Overview**

- **Built for**: AWS AI Agent Global Hackathon 2025
- **Core Value**: Personalized career guidance and job matching
- **Technology**: AWS Bedrock AgentCore + FastAPI + Next.js + ML Analysis

## System Architecture
```mermaid
flowchart TD
  %% Frontend
  subgraph "Frontend Layer"
    User["[Next.js Frontend]<br>User Web App"]
    User -->|"HTTPS + Auth"| APIGW["[AWS API Gateway]<br>Entry / Load Balancer"]
  end

  %% Backend
  subgraph "Application Backend Layer"
    APIGW --> BFF["[FastAPI]<br>Backend API"]
    BFF --> Cognito["[AWS Cognito]<br>Authentication & Identity"]
    BFF -->|calls| AgentAPI["**[Amazon Bedrock AgentCore]**<br>Agent API Endpoint"]
    BFF -->|calls| JobRecommender["Job Matching API<br>(Internal Python Service)"]
  end

  %% Agent
  subgraph "Agent Layer"
    AgentAPI --> AgentRuntime["Agent Runtime<br>(AgentCore / Python)"]
    AgentRuntime --> ToolInvoker["Tool Invoker<br>(Lambdas & External APIs)"]
    AgentRuntime --> Memory["Memory Manager<br>(VectorDB / DynamoDB)"]
    AgentRuntime --> Bedrock["**[Amazon Bedrock]**<br>LLMs for Reasoning & Generation"]
    AgentRuntime --> Secrets["**[AWS Secrets Manager]**<br>Credentials"]
    AgentRuntime --> Observability["**[CloudWatch / X-Ray]**<br>Monitoring"]
    Observability --> DevOps["**[Grafana / Alerts / PagerDuty]**"]
  end

  %% Tools & Data
  subgraph "Tools & Data Layer"
    ToolInvoker --> Lambdas["**[AWS Lambda Functions]**<br>• Resume Parser (Textract)<br>• Job Fetcher (OpenSearch/Adzuna)<br>• Company Info (Crunchbase)<br>• Scoring / Embeddings<br>• Apply Simulator"]
    Lambdas --> S3["**[AWS S3]**<br>Resumes / Artifacts"]
    Lambdas --> VectorDB["Vector DB / Pinecone / OpenSearch"]
  end

  %% Persistence
  subgraph "Persistence Layer"
    Memory --> DynamoDB["**[AWS DynamoDB]**<br>User Contexts & Preferences"]
    VectorDB --> Memory
  end
  ```
## 🚀 **Quick Start**

### **1. Setup Development Environment**
```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
# Set up PYTHONPATH
export PYTHONPATH=backend/app/:$PYTHONPATH

# Start the FastAPI backend service
python backend/app/main.py

# interact with LLM. AgentCore should utilize the API to query results (via tools)
make agentdeploy
agentcore invoke '{"prompt": "software engineering jobs"}'

# Or test locally
make configure
agentcore launch --local
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# Install frontend dependencies
cd frontend && npm install && cd ..
# Start the frontend (new terminal)
cd frontend && npm run dev
```


Type enter when being asked on deployment details. Theoretically we should be able to invoke agent response using commands such as `agentcore invoke '{"prompt": "Find me real 3 job openings for software engineer intern with apply urls"}'`

### **3. Test the System**
```bash
[TODO]
# Test resume upload
curl -X POST "http://localhost:8000/api/resume/upload" \
  -F "file=@sample_resume.pdf"

# Test job recommendations
curl -X GET "http://localhost:8000/api/jobs/recommendations?user_id=123"
```

## 🏗️ **Project Structure**

```
careercompass-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── routers/          # API endpoints
│   │   ├── core/             # Configuration & database
│   │   ├── services/         # Business logic
│   │   ├── agents/           # AI agents
│   │   └── models/           # Data models
│   └── requirements.txt
├── frontend/                  # Next.js frontend
│   ├── pages/                # Next.js pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities
│   └── package.json
├── infra/                    # Infrastructure
│   ├── terraform/            # AWS infrastructure
│   └── ecs/                  # Container orchestration
├── scripts/                  # Utility scripts
└── docs/                     # Documentation
```

## 🎯 **Core Features**

### **Resume Analysis**
- **PDF Processing**: Extract text and structure from resumes
- **Skill Extraction**: Identify technical and soft skills
- **Experience Analysis**: Parse work history and achievements
- **Education Parsing**: Extract educational background

### **Job Matching**
- **API Integration**: Crunchbase, LinkedIn, Indeed, Greenhouse
- **Skill Matching**: Match user skills to job requirements
- **Company Analysis**: Research company culture and growth
- **Salary Insights**: Market rate analysis and negotiation tips

### **Career Guidance**
- **Skill Gap Analysis**: Identify missing skills for target roles
- **Transition Roadmap**: Step-by-step career progression plan
- **Industry Insights**: Market trends and opportunities
- **Personalized Recommendations**: AI-powered career advice

### **AWS Bedrock Integration**
- **Autonomous Agent**: Orchestrates analysis and recommendations
- **Natural Language**: Conversational career guidance
- **Reasoning Engine**: Complex decision-making for career paths
- **Multi-step Workflows**: Resume → Analysis → Matching → Roadmap

## 🏆 **Hackathon Alignment**

| Criterion                        | Score | Implementation                              |
|----------------------------------|-------|---------------------------------------------|
| **Potential Value/Impact (20%)** | ✅     | Career guidance for millions of job seekers |
| **Creativity (10%)**             | ✅     | Novel AI agent for career development       |
| **Technical Execution (50%)**    | ✅     | Multi-service AWS architecture with Bedrock |
| **Functionality (10%)**          | ✅     | End-to-end career guidance system           |
| **Demo Presentation (10%)**      | ✅     | Live resume analysis and job matching       |

## 🔧 **Technology Stack**

### **Frontend**
- **Next.js**: React framework with SSR
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization
- **TypeScript**: Type-safe development

### **Backend**
- **FastAPI**: High-performance Python API
- **PostgreSQL**: Relational database
- **Redis**: Caching and session storage
- **AWS Bedrock**: AI reasoning and analysis

### **AI/ML**
- **AWS Bedrock AgentCore**: Autonomous career guidance
- **spaCy**: Resume text processing
- **Sentence Transformers**: Skill matching
- **Custom ML Models**: Career path prediction

### **Infrastructure**
- **AWS ECS Fargate**: Container orchestration
- **API Gateway**: API management
- **S3**: File storage
- **CloudWatch**: Monitoring and logging

## 🚀 **Next Steps**

1. **Setup environment**: `./scripts/setup.sh`
2. **Test resume upload**: Upload sample resume
3. **Deploy to AWS**: `cd infra/terraform && terraform apply`
4. **Practice demo**: Live resume analysis and job matching

---

**Ready to revolutionize career guidance!** 🎉


## Notes
Making agents utilize the "services" via python script importing modules is really hard, require hacking the dockerfile after agentcore configure. Not sure if this is what AgentCore is supposed to be.
```
─────────────────────────────────────────────────────── Agent Status: main_agent ───────────────────────────────────────────────────────╮
│ Ready - Agent deployed and endpoint available                                                                                          │
│                                                                                                                                        │
│ Agent Details:                                                                                                                         │
│ Agent Name: main_agent                                                                                                                 │
│ Agent ARN: arn:aws:bedrock-agentcore:us-east-1:355444226013:runtime/main_agent-B3Kog7FjWn                                              │
│ Endpoint: DEFAULT (READY)                                                                                                              │
│ Region: us-east-1 | Account: 355444226013                                                                                              │
│                                                                                                                                        │
│ Memory: STM only (memory_ymkys-OsxFMnFs19)                                                                                             │
│                                                                                                                                        │
│ Deployment Info:                                                                                                                       │
│ Created: 2025-10-18 06:38:32.930214+00:00                                                                                              │
│ Last Updated: 2025-10-19 00:22:27.970153+00:00                                                                                         │
│                                                                                                                                        │
│ 📋 CloudWatch Logs:                                                                                                                    │
│    /aws/bedrock-agentcore/runtimes/main_agent-B3Kog7FjWn-DEFAULT --log-stream-name-prefix "2025/10/19/[runtime-logs]"                  │
│    /aws/bedrock-agentcore/runtimes/main_agent-B3Kog7FjWn-DEFAULT --log-stream-names "otel-rt-logs"                                     │
│                                                                                                                                        │
│ 🔍 GenAI Observability Dashboard:                                                                                                      │
│    https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core                                     │
│                                                                                                                                        │
│ ⏱️  Note: Observability data may take up to 10 minutes to appear after first launch                                                     │
│                                                                                                                                        │
│ 💡 Tail logs with:                                                                                                                     │
│    aws logs tail /aws/bedrock-agentcore/runtimes/main_agent-B3Kog7FjWn-DEFAULT --log-stream-name-prefix "2025/10/19/[runtime-logs]"    │
│ --follow                                                                                                                               │
│    aws logs tail /aws/bedrock-agentcore/runtimes/main_agent-B3Kog7FjWn-DEFAULT --log-stream-name-prefix "2025/10/19/[runtime-logs]"    │
│ --since 1h                                                                                                                             │
│                                                                                                                                        │
│ Ready to invoke:                                                                                                                       │
│    agentcore invoke '{"prompt": "Hello"}'
```
