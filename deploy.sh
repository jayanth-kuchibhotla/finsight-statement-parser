#!/bin/bash

set -e

echo "Deploying infrastructure..."

# Build Lambda packages first
echo "Running build script..."
./build.sh

# Navigate to Terraform directory
cd terraform

echo "Initializing Terraform..."
terraform init

echo "Validating Terraform..."
terraform validate

echo "Planning Terraform..."
terraform plan -var-file="terraform.tfvars"

echo "Applying Terraform..."
terraform apply -var-file="terraform.tfvars" -auto-approve

cd ..

echo "Deployment complete."