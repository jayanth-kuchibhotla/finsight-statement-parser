aws_account_id              =   "145116561323"

aws_region                  =   "ap-south-1"

project_name                =   "finsight-statement-parser"

lambda_runtime              =   "python3.12"

lambda_handler              =   "lambda_function.lambda_handler"

lambda_zip_parser           =   "../Statement-Parser/parser.zip"

lambda_zip_presigned_url    =   "../Statement-Service-Presigned-URL-Generation/presigned_url.zip"

lambda_zip_s3_trigger       =   "../S3-Trigger-Service/s3_trigger.zip"

lambda_zip_bedrock_parser   =   "../Bedrock-Parser/bedrock_parser.zip"

lambda_zip_results_api      =   "../Results-API/results_api.zip"

api_allowed_origins         =   ["http://localhost:3000"] # Update to Vercel domain in production

billing_alert_email         =   "jayanth.kuchibhotla@gmail.com"
