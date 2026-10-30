resource "aws_apigatewayv2_api" "statement_parser_api_gateway" {
  name          = "statement-parser-api-gateway"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = var.api_allowed_origins
    allow_methods = ["*"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_integration" "statement_parser_presigned_url_integration" {
  api_id           = aws_apigatewayv2_api.statement_parser_api_gateway.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.presigned_url_generation.invoke_arn
}

resource "aws_apigatewayv2_integration" "results_api_integration" {
  api_id           = aws_apigatewayv2_api.statement_parser_api_gateway.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.results_api.invoke_arn
}

resource "aws_apigatewayv2_route" "statement_parser_presigned_url_route" {
  api_id    = aws_apigatewayv2_api.statement_parser_api_gateway.id
  route_key = "POST /generate-presigned-url"
  target    = "integrations/${aws_apigatewayv2_integration.statement_parser_presigned_url_integration.id}"
}

resource "aws_apigatewayv2_route" "results_api_route" {
  api_id    = aws_apigatewayv2_api.statement_parser_api_gateway.id
  route_key = "GET /results/{statement_id}"
  target    = "integrations/${aws_apigatewayv2_integration.results_api_integration.id}"
}

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/vendedlogs/api-gateway/${var.project_name}-api"
  retention_in_days = 30
}

resource "aws_apigatewayv2_stage" "statement_parser_default_stage" {
  api_id      = aws_apigatewayv2_api.statement_parser_api_gateway.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      "requestId"          = "$context.requestId"
      "ip"                 = "$context.identity.sourceIp"
      "requestTime"        = "$context.requestTime"
      "httpMethod"         = "$context.httpMethod"
      "routeKey"           = "$context.routeKey"
      "error"              = "$context.error.message"
      "integrationLatency" = "$context.integrationLatency"
      "protocol"           = "$context.protocol"
      "responseLatency"    = "$context.responseLatency"
      "responseLength"     = "$context.responseLength"
      "status"             = "$context.status"
    })
  }
}
