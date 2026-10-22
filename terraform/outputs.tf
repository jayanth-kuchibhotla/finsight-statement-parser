output "api_endpoint" {
  value = aws_apigatewayv2_api.statement_parser_api_gateway.api_endpoint
}

resource "local_file" "env_file" {
  content  = <<-EOT
    REACT_APP_API_GATEWAY_ENDPOINT=${aws_apigatewayv2_api.statement_parser_api_gateway.api_endpoint}
    REACT_APP_RESULTS_ENDPOINT=${aws_apigatewayv2_api.statement_parser_api_gateway.api_endpoint}/results
  EOT
  filename = "../frontend/.env"
}
