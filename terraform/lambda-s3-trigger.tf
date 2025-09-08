data "aws_iam_policy_document" "s3_trigger_lambda_policy" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.input_queue.arn]
  }
}

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

resource "aws_iam_role" "s3_trigger_lambda_role" {
  name               = "${var.project_name}-s3-trigger-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy" "s3_trigger_lambda_policy" {
  name   = "${var.project_name}-s3-trigger-policy"
  role   = aws_iam_role.s3_trigger_lambda_role.id
  policy = data.aws_iam_policy_document.s3_trigger_lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "s3_trigger_lambda_basic_execution" {
  role       = aws_iam_role.s3_trigger_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
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
