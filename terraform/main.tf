provider "aws" {
  region                  = "ap-south-1"
  skip_metadata_api_check = true
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4.0"
    }
  }

  backend "s3" {
    bucket         = "fintech-statement-parser-bucket"
    key            = "terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "statement-parser-table"
  }
}
