# CompanyRadar: Autonomous Market Intelligence Agent

An AI agent that continuously scans, summarizes, and visualizes the strategic moves, partnerships, and product focus areas of major tech companies — building a similarity graph that updates itself using reasoning and real-time data.

## 🎯 Hackathon Alignment

This project is designed for the AWS AI Agent Global Hackathon and meets all requirements:

- **Autonomous AI Agent**: Uses reasoning LLMs for decision-making and task execution
- **AWS Integration**: Built with Bedrock AgentCore, SageMaker, and other AWS services
- **Real-world Impact**: Helps analysts, investors, and founders understand market trends
- **Technical Excellence**: Multi-service architecture with live data pipeline

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   AWS Bedrock    │    │   Visualization │
│   (News, APIs)  │───▶│   AgentCore      │───▶│   (React App)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   SageMaker      │
                       │   (Clustering)   │
                       └──────────────────┘
```

## 🚀 Quick Start

1. **Prerequisites**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up AWS credentials
   aws configure
   ```

2. **Deploy Infrastructure**
   ```bash
   # Deploy AWS resources
   python scripts/deploy_infrastructure.py
   ```

3. **Run the Agent**
   ```bash
   # Start the autonomous agent
   python src/agent/main.py
   ```

4. **View Results**
   ```bash
   # Start the visualization frontend
   cd frontend && npm start
   ```

## 📁 Project Structure

```
company_radar/
├── src/
│   ├── agent/           # Core AI agent logic
│   ├── data/            # Data ingestion and processing
│   ├── ml/              # Machine learning models
│   └── api/             # REST API endpoints
├── frontend/            # React visualization app
├── infrastructure/      # AWS CDK/Terraform configs
├── scripts/             # Deployment and utility scripts
└── docs/               # Documentation
```

## 🎯 Key Features

- **Autonomous Reasoning**: Agent plans and executes data collection tasks
- **Real-time Data**: Integrates with news APIs, job boards, and company databases
- **AI Clustering**: Uses embeddings to identify company similarities
- **Interactive Visualization**: Dynamic graphs showing market relationships
- **Continuous Learning**: Agent improves its understanding over time

## 🏆 Hackathon Criteria Alignment

| Criterion | Score | Implementation |
|-----------|-------|----------------|
| **Potential Value/Impact (20%)** | ✅ | Helps analysts understand market trends at scale |
| **Creativity (10%)** | ✅ | Novel autonomous agent for market intelligence |
| **Technical Execution (50%)** | ✅ | Multi-service AWS architecture with reasoning |
| **Functionality (10%)** | ✅ | Live data pipeline with interactive visualization |
| **Demo Presentation (10%)** | ✅ | End-to-end agent workflow demonstration |

## 🔧 AWS Services Used

- **Amazon Bedrock AgentCore**: Task planning and reasoning
- **Amazon Bedrock**: LLM foundation (Claude/Mistral)
- **Amazon SageMaker**: ML clustering and embeddings
- **AWS Lambda**: Serverless compute for data processing
- **Amazon S3**: Data storage and model artifacts
- **Amazon DynamoDB**: Real-time data storage
- **Amazon API Gateway**: REST API endpoints
- **Amazon CloudWatch**: Monitoring and logging

## 📊 Demo Scenarios

1. **Agent Planning**:** "What companies should I monitor this week?"
2. **Data Collection**:** Autonomous gathering from multiple sources
3. **AI Analysis**:** Clustering companies by strategic similarity
4. **Visualization**:** Interactive graph showing market relationships
5. **Query Interface**:** "Show me AI companies converging on infrastructure"

## 🚀 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.
