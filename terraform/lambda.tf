resource "aws_lambda_function" "parser" {
  function_name = "${var.project_name}"
  filename      = var.lambda_zip_parser
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.parser_lambda_role.arn
  timeout       = 900

  environment {
    variables = {
      S3_BUCKET_NAME        = aws_s3_bucket.statement_parser_data.bucket
      BEDROCK_QUEUE_URL     = aws_sqs_queue.bedrock_queue.url
      LOG_LEVEL             = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.parser_lambda_policy]
}

resource "aws_lambda_event_source_mapping" "parser_sqs_mapping" {
  event_source_arn = aws_sqs_queue.input_queue.arn
  function_name    = aws_lambda_function.parser.arn
  batch_size       = 5
  enabled          = true
}

resource "aws_lambda_function" "s3_trigger" {
  function_name = "${var.project_name}-s3-trigger"
  filename      = var.lambda_zip_s3_trigger
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.s3_trigger_lambda_role.arn
  timeout       = 60

  environment {
    variables = {
      INPUT_QUEUE_URL = aws_sqs_queue.input_queue.url
      LOG_LEVEL      = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.s3_trigger_lambda_policy]
}

resource "aws_lambda_permission" "s3_trigger_permission" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.statement_parser_data.arn
}

resource "aws_lambda_function" "presigned_url_generation" {
  function_name = "${var.project_name}-presigned-url-generation"
  filename      = var.lambda_zip_presigned_url
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.presigned_url_lambda_role.arn
  timeout       = 60

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.statement_parser_data.bucket
      LOG_LEVEL      = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.presigned_url_lambda_policy]
}

resource "aws_lambda_function" "bedrock_parser" {
  function_name = "${var.project_name}-bedrock-parser"
  filename      = var.lambda_zip_bedrock_parser
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.bedrock_lambda_role.arn
  timeout       = 900

  environment {
    variables = {
      STATEMENTS_TABLE  = aws_dynamodb_table.statements.name
      TRANSACTIONS_TABLE = aws_dynamodb_table.transactions.name
      LOG_LEVEL = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.bedrock_lambda_policy]
}

resource "aws_lambda_event_source_mapping" "bedrock_sqs_mapping" {
  event_source_arn = aws_sqs_queue.bedrock_queue.arn
  function_name    = aws_lambda_function.bedrock_parser.arn
  batch_size       = 5
  enabled          = true
}

resource "aws_lambda_function" "results_api" {
  function_name = "${var.project_name}-results-api"
  filename      = var.lambda_zip_results_api
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.results_api_lambda_role.arn
  timeout       = 60

  environment {
    variables = {
      STATEMENTS_TABLE  = aws_dynamodb_table.statements.name
      TRANSACTIONS_TABLE = aws_dynamodb_table.transactions.name
      LOG_LEVEL                        = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.results_api_lambda_policy]
}

resource "aws_lambda_permission" "results_api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvokeResults"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.results_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.statement_parser_api_gateway.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.presigned_url_generation.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.statement_parser_api_gateway.execution_arn}/*/*"
}
