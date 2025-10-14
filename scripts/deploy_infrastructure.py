#!/usr/bin/env python3
"""
Deployment script for CompanyRadar infrastructure.

This script deploys the complete AWS infrastructure stack using CDK
and sets up all necessary services for the autonomous market intelligence agent.
"""

import os
import sys
import json
import boto3
import subprocess
from pathlib import Path
from typing import Dict, List
import argparse


class CompanyRadarDeployer:
    """
    Deploys CompanyRadar infrastructure to AWS.

    This class handles the complete deployment process including:
    - CDK stack deployment
    - Bedrock agent configuration
    - SageMaker model setup
    - API endpoint configuration
    """

    def __init__(self, config: Dict):
        """Initialize the deployer with configuration."""
        self.config = config
        self.region = config.get('region', 'us-east-1')
        self.account_id = self._get_account_id()

        # Initialize AWS clients
        self.cdk_client = boto3.client('cloudformation', region_name=self.region)
        self.bedrock_client = boto3.client('bedrock', region_name=self.region)
        self.sagemaker_client = boto3.client('sagemaker', region_name=self.region)

        print(f"🚀 CompanyRadar Deployer initialized for region {self.region}")

    def _get_account_id(self) -> str:
        """Get AWS account ID."""
        try:
            sts_client = boto3.client('sts')
            return sts_client.get_caller_identity()['Account']
        except Exception as e:
            print(f"❌ Failed to get AWS account ID: {e}")
            sys.exit(1)

    def deploy_infrastructure(self):
        """Deploy the complete infrastructure stack."""
        try:
            print("🏗️ Deploying CompanyRadar infrastructure...")

            # Deploy CDK stack
            self._deploy_cdk_stack()

            # Configure Bedrock agent
            self._configure_bedrock_agent()

            # Set up SageMaker models
            self._setup_sagemaker_models()

            # Configure API endpoints
            self._configure_api_endpoints()

            # Run health checks
            self._run_health_checks()

            print("✅ Infrastructure deployment completed successfully!")

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

    def _deploy_cdk_stack(self):
        """Deploy the CDK stack."""
        try:
            print("📦 Deploying CDK stack...")

            # Change to infrastructure directory
            infra_dir = Path(__file__).parent.parent / "infrastructure"
            os.chdir(infra_dir)

            # Install dependencies
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

            # Bootstrap CDK (if needed)
            subprocess.run(["cdk", "bootstrap"], check=True)

            # Deploy the stack
            subprocess.run(["cdk", "deploy", "--require-approval", "never"], check=True)

            print("✅ CDK stack deployed successfully")

        except subprocess.CalledProcessError as e:
            print(f"❌ CDK deployment failed: {e}")
            raise

    def _configure_bedrock_agent(self):
        """Configure Bedrock agent for autonomous reasoning."""
        try:
            print("🤖 Configuring Bedrock agent...")

            # Create agent configuration
            agent_config = {
                "agentName": "CompanyRadarAgent",
                "description": "Autonomous market intelligence agent for company analysis",
                "foundationModel": "anthropic.claude-3-sonnet-20240229-v1:0",
                "instruction": """
                You are an autonomous market intelligence agent. Your role is to:
                1. Analyze company data and identify strategic similarities
                2. Plan data collection tasks based on market context
                3. Generate insights about market trends and convergence
                4. Provide reasoning for your analysis and recommendations

                Always provide structured, actionable insights with clear reasoning.
                """,
                "actionGroups": [
                    {
                        "actionGroupName": "DataCollection",
                        "description": "Actions for collecting company data",
                        "actionGroupExecutor": {
                            "lambda": "arn:aws:lambda:{}:{}:function:company-radar-data-collector".format(
                                self.region, self.account_id
                            )
                        }
                    },
                    {
                        "actionGroupName": "SimilarityAnalysis",
                        "description": "Actions for analyzing company similarities",
                        "actionGroupExecutor": {
                            "lambda": "arn:aws:lambda:{}:{}:function:company-radar-similarity-analyzer".format(
                                self.region, self.account_id
                            )
                        }
                    }
                ]
            }

            # Create the agent
            response = self.bedrock_client.create_agent(**agent_config)
            agent_id = response['agent']['agentId']

            print(f"✅ Bedrock agent configured with ID: {agent_id}")

            # Store agent ID in config
            self.config['bedrock_agent_id'] = agent_id

        except Exception as e:
            print(f"❌ Failed to configure Bedrock agent: {e}")
            raise

    def _setup_sagemaker_models(self):
        """Set up SageMaker models for ML processing."""
        try:
            print("🧠 Setting up SageMaker models...")

            # Create model for embeddings
            embedding_model_config = {
                "ModelName": "company-radar-embeddings",
                "PrimaryContainer": {
                    "Image": "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.0.0-transformers4.28.1-cpu-py39-ubuntu20.04",
                    "ModelDataUrl": "s3://company-radar-models/embeddings/model.tar.gz",
                    "Environment": {
                        "HF_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2",
                        "HF_TASK": "feature-extraction"
                    }
                },
                "ExecutionRoleArn": f"arn:aws:iam::{self.account_id}:role/CompanyRadarSageMakerRole"
            }

            # Create the model
            self.sagemaker_client.create_model(**embedding_model_config)

            # Create endpoint configuration
            endpoint_config = {
                "EndpointConfigName": "company-radar-embeddings-config",
                "ProductionVariants": [
                    {
                        "VariantName": "primary",
                        "ModelName": "company-radar-embeddings",
                        "InitialInstanceCount": 1,
                        "InstanceType": "ml.t2.medium"
                    }
                ]
            }

            self.sagemaker_client.create_endpoint_config(**endpoint_config)

            # Create endpoint
            endpoint_config = {
                "EndpointName": "company-radar-embeddings",
                "EndpointConfigName": "company-radar-embeddings-config"
            }

            self.sagemaker_client.create_endpoint(**endpoint_config)

            print("✅ SageMaker models configured successfully")

        except Exception as e:
            print(f"❌ Failed to setup SageMaker models: {e}")
            raise

    def _configure_api_endpoints(self):
        """Configure API Gateway endpoints."""
        try:
            print("🔗 Configuring API endpoints...")

            # Get API Gateway URL from CloudFormation stack
            stack_name = "CompanyRadarStack"
            response = self.cdk_client.describe_stacks(StackName=stack_name)

            outputs = response['Stacks'][0]['Outputs']
            api_url = None

            for output in outputs:
                if output['OutputKey'] == 'APIGatewayURL':
                    api_url = output['OutputValue']
                    break

            if api_url:
                print(f"✅ API Gateway URL: {api_url}")
                self.config['api_url'] = api_url
            else:
                print("⚠️ API Gateway URL not found in stack outputs")

        except Exception as e:
            print(f"❌ Failed to configure API endpoints: {e}")
            raise

    def _run_health_checks(self):
        """Run health checks on deployed infrastructure."""
        try:
            print("🏥 Running health checks...")

            # Check CloudFormation stack status
            stack_name = "CompanyRadarStack"
            response = self.cdk_client.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']

            if stack_status == 'CREATE_COMPLETE':
                print("✅ CloudFormation stack is healthy")
            else:
                print(f"⚠️ CloudFormation stack status: {stack_status}")

            # Check Lambda functions
            lambda_client = boto3.client('lambda', region_name=self.region)
            functions = [
                'company-radar-data-collector',
                'company-radar-similarity-analyzer',
                'company-radar-agent-orchestrator'
            ]

            for function_name in functions:
                try:
                    response = lambda_client.get_function(FunctionName=function_name)
                    print(f"✅ Lambda function {function_name} is healthy")
                except Exception as e:
                    print(f"❌ Lambda function {function_name} health check failed: {e}")

            # Check DynamoDB table
            dynamodb_client = boto3.client('dynamodb', region_name=self.region)
            try:
                response = dynamodb_client.describe_table(TableName='company-radar-data')
                table_status = response['Table']['TableStatus']
                if table_status == 'ACTIVE':
                    print("✅ DynamoDB table is healthy")
                else:
                    print(f"⚠️ DynamoDB table status: {table_status}")
            except Exception as e:
                print(f"❌ DynamoDB table health check failed: {e}")

            # Check S3 bucket
            s3_client = boto3.client('s3', region_name=self.region)
            try:
                bucket_name = f"company-radar-data-{self.account_id}"
                response = s3_client.head_bucket(Bucket=bucket_name)
                print("✅ S3 bucket is healthy")
            except Exception as e:
                print(f"❌ S3 bucket health check failed: {e}")

            print("✅ Health checks completed")

        except Exception as e:
            print(f"❌ Health checks failed: {e}")
            raise

    def save_config(self):
        """Save the updated configuration."""
        try:
            config_file = Path(__file__).parent.parent / "config" / "deployment.json"
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

            print(f"✅ Configuration saved to {config_file}")

        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            raise


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy CompanyRadar infrastructure')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--config', help='Configuration file path')

    args = parser.parse_args()

    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'region': args.region,
            'bedrock_agent_id': None,
            'api_url': None
        }

    # Create deployer
    deployer = CompanyRadarDeployer(config)

    # Deploy infrastructure
    deployer.deploy_infrastructure()

    # Save configuration
    deployer.save_config()

    print("\n🎉 CompanyRadar infrastructure deployment completed!")
    print("\nNext steps:")
    print("1. Configure API keys in environment variables")
    print("2. Start the autonomous agent: python src/agent/main.py")
    print("3. Launch the frontend: cd frontend && npm start")
    print("4. Access the dashboard at the API Gateway URL")


if __name__ == "__main__":
    main()

