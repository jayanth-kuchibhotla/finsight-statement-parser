resource "aws_dynamodb_table" "statements" {
  name         = "finsight-statements"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "statement_id"

  attribute {
    name = "statement_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled = true
  }
}

resource "aws_dynamodb_table" "transactions" {
  name         = "finsight-transactions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "transaction_id"
  range_key    = "statement_id"

  attribute {
    name = "transaction_id"
    type = "S"
  }

  attribute {
    name = "statement_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled = true
  }

  global_secondary_index {
    name            = "StatementIDIndex"
    hash_key        = "statement_id"
    range_key       = "transaction_id"
    projection_type = "ALL"
  }
}
