"""
AWS CDK Infrastructure for CompanyRadar

Deploys the complete AWS infrastructure stack for the autonomous
market intelligence agent including Bedrock, SageMaker, S3, DynamoDB, and Lambda.
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_bedrock as bedrock,
    aws_sagemaker as sagemaker,
    aws_cloudwatch as cloudwatch,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class CompanyRadarStack(Stack):
    """
    AWS CDK Stack for CompanyRadar infrastructure.
    
    This stack deploys all necessary AWS services for the autonomous
    market intelligence agent including:
    - Bedrock for AI reasoning
    - SageMaker for ML models
    - S3 for data storage
    - DynamoDB for real-time data
    - Lambda for serverless compute
    - API Gateway for REST endpoints
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for data storage
        self.data_bucket = s3.Bucket(
            self, "CompanyRadarDataBucket",
            bucket_name=f"company-radar-data-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Create DynamoDB table for real-time data
        self.data_table = dynamodb.Table(
            self, "CompanyRadarDataTable",
            table_name="company-radar-data",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Create IAM role for Lambda functions
        self.lambda_role = iam.Role(
            self, "CompanyRadarLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ],
            inline_policies={
                "CompanyRadarPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                self.data_bucket.bucket_arn,
                                f"{self.data_bucket.bucket_arn}/*"
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "dynamodb:GetItem",
                                "dynamodb:PutItem",
                                "dynamodb:UpdateItem",
                                "dynamodb:DeleteItem",
                                "dynamodb:Query",
                                "dynamodb:Scan"
                            ],
                            resources=[self.data_table.table_arn]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeAgent",
                                "bedrock:GetAgent",
                                "bedrock:ListAgents"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sagemaker:InvokeEndpoint",
                                "sagemaker:DescribeEndpoint",
                                "sagemaker:ListEndpoints"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )
        
        # Create Lambda function for data collection
        self.data_collector_lambda = lambda_.Function(
            self, "DataCollectorLambda",
            function_name="company-radar-data-collector",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="data_collector.handler",
            code=lambda_.Code.from_asset("src/lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(15),
            memory_size=1024,
            environment={
                "S3_BUCKET": self.data_bucket.bucket_name,
                "DYNAMODB_TABLE": self.data_table.table_name,
                "NEWS_API_KEY": "your-news-api-key",
                "LINKEDIN_API_KEY": "your-linkedin-api-key",
                "CRUNCHBASE_API_KEY": "your-crunchbase-api-key"
            }
        )
        
        # Create Lambda function for similarity analysis
        self.similarity_analyzer_lambda = lambda_.Function(
            self, "SimilarityAnalyzerLambda",
            function_name="company-radar-similarity-analyzer",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="similarity_analyzer.handler",
            code=lambda_.Code.from_asset("src/lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(10),
            memory_size=2048,
            environment={
                "S3_BUCKET": self.data_bucket.bucket_name,
                "DYNAMODB_TABLE": self.data_table.table_name,
                "SAGEMAKER_ENDPOINT": "company-radar-embeddings"
            }
        )
        
        # Create Lambda function for agent orchestration
        self.agent_orchestrator_lambda = lambda_.Function(
            self, "AgentOrchestratorLambda",
            function_name="company-radar-agent-orchestrator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="agent_orchestrator.handler",
            code=lambda_.Code.from_asset("src/lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(30),
            memory_size=1024,
            environment={
                "S3_BUCKET": self.data_bucket.bucket_name,
                "DYNAMODB_TABLE": self.data_table.table_name,
                "BEDROCK_AGENT_ID": "your-bedrock-agent-id"
            }
        )
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "CompanyRadarAPI",
            rest_api_name="CompanyRadar API",
            description="API for CompanyRadar autonomous market intelligence agent",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Add API endpoints
        self._create_api_endpoints()
        
        # Create EventBridge rule for scheduled execution
        self.schedule_rule = events.Rule(
            self, "CompanyRadarSchedule",
            schedule=events.Schedule.rate(Duration.hours(1)),
            description="Schedule for CompanyRadar autonomous agent execution"
        )
        
        # Add targets to the schedule
        self.schedule_rule.add_target(
            targets.LambdaFunction(self.agent_orchestrator_lambda)
        )
        
        # Create CloudWatch dashboard
        self._create_cloudwatch_dashboard()
        
        # Output important values
        CfnOutput(
            self, "DataBucketName",
            value=self.data_bucket.bucket_name,
            description="S3 bucket for storing company data"
        )
        
        CfnOutput(
            self, "DataTableName",
            value=self.data_table.table_name,
            description="DynamoDB table for real-time data"
        )
        
        CfnOutput(
            self, "APIGatewayURL",
            value=self.api.url,
            description="API Gateway URL for the application"
        )
    
    def _create_api_endpoints(self):
        """Create API Gateway endpoints for the application."""
        
        # Companies endpoint
        companies_resource = self.api.root.add_resource("companies")
        companies_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.data_collector_lambda,
                request_templates={"application/json": '{"statusCode": "200"}'}
            )
        )
        
        # Similarity analysis endpoint
        similarity_resource = self.api.root.add_resource("similarity")
        similarity_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.similarity_analyzer_lambda,
                request_templates={"application/json": '{"statusCode": "200"}'}
            )
        )
        
        # Agent status endpoint
        agent_resource = self.api.root.add_resource("agent")
        agent_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.agent_orchestrator_lambda,
                request_templates={"application/json": '{"statusCode": "200"}'}
            )
        )
        
        # Insights endpoint
        insights_resource = self.api.root.add_resource("insights")
        insights_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.similarity_analyzer_lambda,
                request_templates={"application/json": '{"statusCode": "200"}'}
            )
        )
    
    def _create_cloudwatch_dashboard(self):
        """Create CloudWatch dashboard for monitoring."""
        
        dashboard = cloudwatch.Dashboard(
            self, "CompanyRadarDashboard",
            dashboard_name="CompanyRadar-Monitoring"
        )
        
        # Add widgets for monitoring
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations",
                left=[self.data_collector_lambda.metric_invocations()],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="Lambda Errors",
                left=[self.data_collector_lambda.metric_errors()],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="DynamoDB Read/Write Capacity",
                left=[self.data_table.metric_consumed_read_capacity_units()],
                right=[self.data_table.metric_consumed_write_capacity_units()],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="S3 Storage",
                left=[self.data_bucket.metric_bucket_size_bytes()],
                width=12,
                height=6
            )
        )

