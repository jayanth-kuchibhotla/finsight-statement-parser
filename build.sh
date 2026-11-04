#!/bin/bash

set -e

echo "Building Lambda packages..."

build_lambda() {
    local name=$1
    local folder=$2
    local zip_name=$3

    echo "Building $name..."

    cd "$folder"
    pip install -r requirements.txt -t package/ --quiet
    cp *.py package/
    
    if [ -d "Parser_Functions" ]; then
        cp -r Parser_Functions package/
    fi

    cd package
    zip -r "../$zip_name" . --quiet
    cd ..
    rm -rf package/
    cd ..

    echo "$name built successfully."
}

build_lambda "S3-Trigger" "S3-Trigger-Service" "s3_trigger.zip"
build_lambda "Presigned-URL" "Statement-Service-Presigned-URL-Generation" "presigned_url.zip"
build_lambda "Statement-Parser" "Statement-Parser" "parser.zip"
build_lambda "Bedrock-Parser" "Bedrock-Parser" "bedrock_parser.zip"
build_lambda "Results-API" "Results-API" "results_api.zip"

echo "All Lambda packages built successfully."