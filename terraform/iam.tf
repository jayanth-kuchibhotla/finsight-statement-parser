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
  # Allow downloading and reading uploaded PDFs
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.statement_parser_data.arn}/uploads/*"]
  }

  # Forwarding statements and transactions to Bedrock Lambda via SQS
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.bedrock_queue.arn]
  }

  # Allow reading from SQS
  statement {
    effect    = "Allow"
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.input_queue.arn]
  }
}

data "aws_iam_policy_document" "bedrock_lambda_policy" {
  # Allow Bedrock Lambda to read from SQS
  statement {
    effect    = "Allow"
    actions   = ["bedrock:InvokeModel"]
    resources = ["*"]
  }

  # Allow items to be written to DynamoDB
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem", "dynamodb:BatchWriteItem"]
    resources = [aws_dynamodb_table.statements.arn, aws_dynamodb_table.transactions.arn]
  }

  # Allow reading from SQS
  statement {
    effect    = "Allow"
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.bedrock_queue.arn]
  }
}

data "aws_iam_policy_document" "results_api_policy" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:Query"]
    resources = [aws_dynamodb_table.statements.arn, aws_dynamodb_table.transactions.arn, "${aws_dynamodb_table.transactions.arn}/index/StatementIDIndex"]
  }
}

resource "aws_iam_role" "parser_lambda_role" {
  name               = "${var.project_name}-parser-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role" "bedrock_lambda_role" {
  name               = "${var.project_name}-bedrock-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role" "results_api_lambda_role" {
  name               = "${var.project_name}-results-api-role"
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

data "aws_iam_policy_document" "presigned_url_lambda_policy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.statement_parser_data.arn}/uploads/*"]
  }
}

resource "aws_iam_role" "presigned_url_lambda_role" {
  name               = "${var.project_name}-presigned-url-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "presigned_url_lambda_basic_execution" {
  role       = aws_iam_role.presigned_url_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "presigned_url_lambda_policy" {
  name   = "${var.project_name}-presigned-url-policy"
  role   = aws_iam_role.presigned_url_lambda_role.id
  policy = data.aws_iam_policy_document.presigned_url_lambda_policy.json
}

data "aws_iam_policy_document" "s3_trigger_lambda_policy" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.input_queue.arn]
  }
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

resource "aws_iam_role_policy" "bedrock_lambda_policy" {
  name   = "${var.project_name}-bedrock-policy"
  role   = aws_iam_role.bedrock_lambda_role.id
  policy = data.aws_iam_policy_document.bedrock_lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "bedrock_lambda_basic_execution" {
  role       = aws_iam_role.bedrock_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "results_api_lambda_policy" {
  name   = "${var.project_name}-results-api-policy"
  role   = aws_iam_role.results_api_lambda_role.id
  policy = data.aws_iam_policy_document.results_api_policy.json
}

resource "aws_iam_role_policy_attachment" "results_api_lambda_basic_execution" {
  role       = aws_iam_role.results_api_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
