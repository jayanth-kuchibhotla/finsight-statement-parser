data "aws_iam_policy_document" "presigned_url_lambda_policy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${data.aws_s3_bucket.statement_parser_data.arn}/uploads/*"]
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

resource "aws_lambda_function" "presigned_url_generation" {
  function_name = "${var.project_name}-presigned-url-generation"
  filename      = var.lambda_zip_presigned_url
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.presigned_url_lambda_role.arn
  timeout       = 60

  environment {
    variables = {
      S3_BUCKET_NAME = data.aws_s3_bucket.statement_parser_data.bucket
      LOG_LEVEL      = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy.presigned_url_lambda_policy]
}
