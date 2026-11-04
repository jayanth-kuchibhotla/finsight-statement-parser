resource "aws_sqs_queue" "input_dlq" {
  name                       = "${var.project_name}-input-dlq"
}

resource "aws_sqs_queue" "input_queue" {
  name                       = "${var.project_name}-input-queue"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.input_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "bedrock_dlq" {
  name                       = "${var.project_name}-bedrock-dlq"
}

resource "aws_sqs_queue" "bedrock_queue" {
  name                       = "${var.project_name}-bedrock-queue"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.bedrock_dlq.arn
    maxReceiveCount     = 3
  })
}
