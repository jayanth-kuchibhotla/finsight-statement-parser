variable "aws_account_id" {
  description = "The AWS account ID where resources will be created."
  type        = string
}

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "A unique name for the project to prefix resources."
  type        = string
  default     = "finsight-statement-parser"
}

variable "lambda_runtime" {
  description = "The runtime environment for the Lambda function."
  type        = string
  default     = "python3.12"
}

variable "lambda_handler" {
  description = "The name of the method within your code that Lambda calls to execute your function."
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "lambda_zip_parser" {
  description = "The path to the deployment package for the parser Lambda function."
  type        = string
  default     = "../Statement-Parser/parser.zip"
}

variable "lambda_zip_s3_trigger" {
  description = "The path to the deployment package for the S3 trigger Lambda function."
  type        = string
  default     = "../S3-Trigger-Service/s3_trigger.zip"
}

variable "lambda_zip_presigned_url" {
  description = "The path to the deployment package for the presigned URL generation Lambda function."
  type        = string
  default     = "../Statement-Service-Presigned-URL-Generation/presigned_url.zip"
}

variable "lambda_zip_bedrock_parser" {
  description = "The path to the deployment package for the Bedrock parser Lambda function."
  type        = string
  default     = "../Bedrock-Parser/bedrock_parser.zip"
}

variable "lambda_zip_results_api" {
  description = "The path to the deployment package for the results API Lambda function."
  type        = string
  default     = "../Results-API/results_api.zip"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "api_allowed_origins" {
  description = "A list of allowed origins for the API Gateway CORS configuration."
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "billing_alert_email" {
  description = "Email address to receive billing alerts."
  type        = string
  default     = "jayanth.kuchibhotla@gmail.com"
}
