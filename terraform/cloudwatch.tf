resource "aws_cloudwatch_log_group" "statement_parser_lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.parser.function_name}"
    retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "s3_trigger_lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.s3_trigger.function_name}"
    retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "presigned_url_lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.presigned_url_generation.function_name}"
    retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "bedrock_parser_lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.bedrock_parser.function_name}"
    retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "results_api_lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.results_api.function_name}"
    retention_in_days = 30
}

resource "aws_sns_topic" "billing_alert" {
    name     = "${var.project_name}-billing-alert"
    provider = aws.us_east_1
}

resource "aws_sns_topic_subscription" "billing_alert_email" {
    topic_arn = aws_sns_topic.billing_alert.arn
    protocol  = "email"
    endpoint  = var.billing_alert_email
    provider  = aws.us_east_1
}

resource "aws_cloudwatch_metric_alarm" "billing_alarm" {
    alarm_name          = "${var.project_name}-billing-alarm"
    comparison_operator = "GreaterThanOrEqualToThreshold"
    evaluation_periods  = 1
    metric_name         = "EstimatedCharges"
    namespace           = "AWS/Billing"
    period              = 21600
    statistic           = "Maximum"
    threshold           = 5.0
    provider            = aws.us_east_1
    alarm_description   = "This alarm turns on when total estimated charges exceed $5"

    alarm_actions       = [aws_sns_topic.billing_alert.arn]
}
