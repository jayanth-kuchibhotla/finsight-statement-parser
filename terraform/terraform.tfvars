aws_account_id = "145116561323"

aws_region = "ap-south-1"

project_name = "fintech-statement-parser"

lambda_runtime = "python3.12"

lambda_handler = "lambda_function.lambda_handler"

lambda_zip_parser = "../Statement-Parser/parser.zip"

lambda_zip_presigned_url = "../Statement-Service-Presigned-URL-Generation/presigned_url.zip"

lambda_zip_s3_trigger = "../S3-Trigger-Service/s3_trigger.zip"

api_allowed_origins = [ "http://localhost:3000", "https://main.d18x02xod9nbm2.amplifyapp.com" ]
