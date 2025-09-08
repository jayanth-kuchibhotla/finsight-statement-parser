data "aws_s3_bucket" "statement_parser_data" {
  bucket = "fintech-statement-parser-bucket"
}

resource "aws_s3_bucket_versioning" "statement_parser_data_versioning" {
  bucket = data.aws_s3_bucket.statement_parser_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_cors_configuration" "statement_parser_data_cors" {
  bucket = data.aws_s3_bucket.statement_parser_data.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "OPTIONS"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "statement_parser_s3_trigger_notification" {
  bucket = data.aws_s3_bucket.statement_parser_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_function.s3_trigger]
}
