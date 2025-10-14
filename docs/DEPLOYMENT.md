# CompanyRadar Deployment Guide

This guide provides step-by-step instructions for deploying the CompanyRadar autonomous market intelligence agent to AWS.

## 🚀 Quick Start

### Prerequisites

1. **AWS Account**: Ensure you have an AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI with your credentials
3. **Python 3.11+**: Required for the agent and deployment scripts
4. **Node.js**: Required for the frontend
5. **CDK**: Install AWS CDK for infrastructure deployment

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/company-radar.git
cd company-radar

# Install Python dependencies
pip install -r requirements.txt

# Install CDK
npm install -g aws-cdk

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 🏗️ Infrastructure Deployment

### 1. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity
```

### 2. Deploy Infrastructure Stack

```bash
# Deploy the complete infrastructure
python scripts/deploy_infrastructure.py --region us-east-1

# Or with custom configuration
python scripts/deploy_infrastructure.py --config config/deployment.json
```

### 3. Configure API Keys

Set up environment variables for external APIs:

```bash
export NEWS_API_KEY="your-news-api-key"
export LINKEDIN_API_KEY="your-linkedin-api-key"
export CRUNCHBASE_API_KEY="your-crunchbase-api-key"
export ALPHA_VANTAGE_KEY="your-alpha-vantage-key"
```

## 🤖 Agent Configuration

### 1. Bedrock Agent Setup

The deployment script automatically configures a Bedrock agent with the following capabilities:

- **Autonomous Reasoning**: Plans tasks based on market context
- **Data Collection**: Orchestrates data gathering from multiple sources
- **Similarity Analysis**: Performs ML-based company clustering
- **Trend Detection**: Identifies market convergence patterns

### 2. SageMaker Models

The infrastructure includes:

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` for company similarity
- **Clustering Algorithm**: K-means and DBSCAN for market segmentation
- **Real-time Inference**: SageMaker endpoints for live analysis

## 📊 Data Sources Configuration

### News APIs
- **NewsAPI**: Primary news source for company announcements
- **Rate Limit**: 1000 requests/day
- **Coverage**: Global news in English

### Job Boards
- **LinkedIn**: Job postings for strategic insights
- **Rate Limit**: 100 requests/hour
- **Data**: Job titles, skills, locations

### Company Databases
- **Crunchbase**: Partnership and funding data
- **Rate Limit**: 50 requests/hour
- **Data**: Investments, partnerships, acquisitions

## 🚀 Running the Agent

### 1. Start the Autonomous Agent

```bash
# Run the main agent
python src/agent/main.py

# Or with custom configuration
python src/agent/main.py --config config/agent.json
```

### 2. Monitor Agent Status

```bash
# Check agent logs
tail -f logs/agent_$(date +%Y-%m-%d).log

# View agent metrics
aws cloudwatch get-metric-statistics \
  --namespace "CompanyRadar" \
  --metric-name "AgentExecutions" \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## 🎨 Frontend Deployment

### 1. Start Development Server

```bash
cd frontend
npm start
```

### 2. Build for Production

```bash
cd frontend
npm run build

# Serve the built files
npx serve -s build -l 3000
```

### 3. Deploy to AWS S3

```bash
# Upload to S3 bucket
aws s3 sync build/ s3://your-frontend-bucket --delete

# Configure CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

## 📈 Monitoring and Maintenance

### 1. CloudWatch Dashboard

Access the monitoring dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=CompanyRadar-Monitoring
```

### 2. Key Metrics

- **Agent Executions**: Number of autonomous cycles completed
- **Data Collection**: API calls and data points gathered
- **Similarity Analysis**: ML model performance and accuracy
- **Error Rates**: System health and reliability

### 3. Logs and Debugging

```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/company-radar"

# View specific log stream
aws logs get-log-events \
  --log-group-name "/aws/lambda/company-radar-data-collector" \
  --log-stream-name "2024/01/15/[$LATEST]abc123"
```

## 🔧 Configuration Options

### Agent Configuration

```json
{
  "agent": {
    "cycle_interval": 3600,
    "max_tasks_per_cycle": 10,
    "priority_threshold": 0.7
  },
  "companies": {
    "target_list": [
      "Amazon", "Google", "Microsoft", "Apple", "Meta",
      "OpenAI", "Anthropic", "Nvidia", "Tesla", "Netflix"
    ]
  },
  "ml": {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "clustering_algorithm": "kmeans",
    "n_clusters": 5
  }
}
```

### API Configuration

```json
{
  "data_sources": {
    "news_api_key": "your-news-api-key",
    "linkedin_api_key": "your-linkedin-api-key",
    "crunchbase_api_key": "your-crunchbase-api-key"
  },
  "aws": {
    "region": "us-east-1",
    "s3_bucket": "company-radar-data",
    "dynamodb_table": "company-radar-data"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Bedrock Agent Not Responding**
   ```bash
   # Check agent status
   aws bedrock-agent get-agent --agent-id your-agent-id

   # Test agent invocation
   aws bedrock-agent-runtime invoke-agent \
     --agent-id your-agent-id \
     --session-id test-session \
     --input-text "Hello"
   ```

2. **SageMaker Endpoint Issues**
   ```bash
   # Check endpoint status
   aws sagemaker describe-endpoint --endpoint-name company-radar-embeddings

   # Test endpoint
   aws sagemaker-runtime invoke-endpoint \
     --endpoint-name company-radar-embeddings \
     --body '{"inputs": "test text"}'
   ```

3. **API Rate Limits**
   ```bash
   # Check current usage
   aws cloudwatch get-metric-statistics \
     --namespace "CompanyRadar" \
     --metric-name "APICalls" \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Sum
   ```

### Performance Optimization

1. **Lambda Memory Tuning**
   - Data Collector: 1024 MB
   - Similarity Analyzer: 2048 MB
   - Agent Orchestrator: 1024 MB

2. **DynamoDB Capacity**
   - Start with On-Demand billing
   - Monitor usage and switch to Provisioned if needed

3. **S3 Storage Classes**
   - Use Intelligent Tiering for cost optimization
   - Set lifecycle policies for old data

## 🔒 Security Considerations

### IAM Permissions

The deployment creates minimal IAM roles with specific permissions:

- **Lambda Execution Role**: Basic execution + S3/DynamoDB access
- **Bedrock Access**: Model invocation and agent management
- **SageMaker Access**: Endpoint invocation and model management

### Data Encryption

- **S3**: Server-side encryption with S3-managed keys
- **DynamoDB**: Encryption at rest enabled
- **Lambda**: Environment variables encrypted

### Network Security

- **VPC**: Optional VPC configuration for Lambda functions
- **Security Groups**: Restrictive inbound/outbound rules
- **API Gateway**: CORS and authentication configured

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CompanyRadar API Documentation](docs/API.md)

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review CloudWatch logs for error details
3. Open an issue on GitHub with detailed error information
4. Contact the development team

---

**Note**: This deployment guide assumes you have appropriate AWS permissions and API keys for external services. Ensure all prerequisites are met before proceeding with deployment.

