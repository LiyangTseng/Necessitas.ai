# CareerCompassAI Infrastructure
# AWS Infrastructure for CareerCompassAI using Terraform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "careercompass-ai"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 Bucket for file uploads
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.project_name}-uploads-${var.environment}"

  tags = {
    Name        = "${var.project_name}-uploads"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# DynamoDB for user data and sessions
resource "aws_dynamodb_table" "user_profiles" {
  name           = "${var.project_name}-user-profiles"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-user-profiles"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "job_sessions" {
  name           = "${var.project_name}-job-sessions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-job-sessions"
    Environment = var.environment
  }
}

# Lambda functions
resource "aws_lambda_function" "resume_parser" {
  filename         = "lambda_functions/resume_parser.zip"
  function_name    = "${var.project_name}-resume-parser"
  role            = aws_iam_role.lambda_role.arn
  handler         = "resume_parser.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.uploads.bucket
      DYNAMODB_TABLE = aws_dynamodb_table.user_profiles.name
    }
  }

  tags = {
    Name        = "${var.project_name}-resume-parser"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "job_fetcher" {
  filename         = "lambda_functions/job_fetcher.zip"
  function_name    = "${var.project_name}-job-fetcher"
  role            = aws_iam_role.lambda_role.arn
  handler         = "job_fetcher.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.job_sessions.name
    }
  }

  tags = {
    Name        = "${var.project_name}-job-fetcher"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "company_researcher" {
  filename         = "lambda_functions/company_researcher.zip"
  function_name    = "${var.project_name}-company-researcher"
  role            = aws_iam_role.lambda_role.arn
  handler         = "company_researcher.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.job_sessions.name
    }
  }

  tags = {
    Name        = "${var.project_name}-company-researcher"
    Environment = var.environment
  }
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.uploads.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.user_profiles.arn,
          aws_dynamodb_table.job_sessions.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "textract:AnalyzeDocument",
          "textract:DetectDocumentText"
        ]
        Resource = "*"
      }
    ]
  })
}

# API Gateway
resource "aws_api_gateway_rest_api" "careercompass_api" {
  name        = "${var.project_name}-api"
  description = "CareerCompassAI API Gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "careercompass_deployment" {
  rest_api_id = aws_api_gateway_rest_api.careercompass_api.id
  stage_name  = var.environment

  depends_on = [
    aws_api_gateway_method.resume_upload,
    aws_api_gateway_method.job_recommendations,
    aws_api_gateway_method.agent_chat
  ]
}

# API Gateway Resources and Methods
resource "aws_api_gateway_resource" "resume" {
  rest_api_id = aws_api_gateway_rest_api.careercompass_api.id
  parent_id   = aws_api_gateway_rest_api.careercompass_api.root_resource_id
  path_part   = "resume"
}

resource "aws_api_gateway_resource" "upload" {
  rest_api_id = aws_api_gateway_rest_api.careercompass_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "upload"
}

resource "aws_api_gateway_method" "resume_upload" {
  rest_api_id   = aws_api_gateway_rest_api.careercompass_api.id
  resource_id   = aws_api_gateway_resource.upload.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "resume_upload" {
  rest_api_id = aws_api_gateway_rest_api.careercompass_api.id
  resource_id = aws_api_gateway_resource.upload.id
  http_method = aws_api_gateway_method.resume_upload.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.resume_parser.invoke_arn
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "api_gateway_resume_parser" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resume_parser.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.careercompass_api.execution_arn}/*/*"
}

# Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "https://${aws_api_gateway_rest_api.careercompass_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.environment}"
}

output "s3_bucket_name" {
  description = "S3 bucket name for uploads"
  value       = aws_s3_bucket.uploads.bucket
}

output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    user_profiles = aws_dynamodb_table.user_profiles.name
    job_sessions  = aws_dynamodb_table.job_sessions.name
  }
}

output "lambda_functions" {
  description = "Lambda function names"
  value = {
    resume_parser      = aws_lambda_function.resume_parser.function_name
    job_fetcher       = aws_lambda_function.job_fetcher.function_name
    company_researcher = aws_lambda_function.company_researcher.function_name
  }
}
