data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "parser_lambda_policy" {
  # Allow reading uploaded PDFs
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${data.aws_s3_bucket.statement_parser_data.arn}/uploads/*"]
  }

  # Allow writing parsed JSON to S3
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${data.aws_s3_bucket.statement_parser_data.arn}/parsed/*"]
  }

  # Allow reading from SQS
  statement {
    effect    = "Allow"
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.input_queue.arn]
  }
}

resource "aws_iam_role" "parser_lambda_role" {
  name               = "${var.project_name}-parser-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "parser_lambda_basic_execution" {
  role       = aws_iam_role.parser_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "parser_lambda_policy" {
  name   = "${var.project_name}-parser-policy"
  role   = aws_iam_role.parser_lambda_role.id
  policy = data.aws_iam_policy_document.parser_lambda_policy.json
}

resource "aws_lambda_function" "parser" {
  function_name = "${var.project_name}"
  filename      = var.lambda_zip_parser
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.parser_lambda_role.arn
  timeout       = 900

  environment {
    variables = {
      S3_BUCKET_NAME        = data.aws_s3_bucket.statement_parser_data.bucket
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
