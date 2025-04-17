#!/bin/bash
set -e  # Exit on any error

# For Terraform external data source usage
if [ -n "$TF_EXTERNAL" ]; then
  # Read input from stdin (terraform passes the query as JSON)
  eval "$(jq -r '@sh "SOURCE_CODE_HASH=\(.source_code_hash) LAMBDA_RUNTIME=\(.lambda_runtime) WORKING_DIR=\(.working_dir)"')"
  
  cd "$WORKING_DIR"
  MODULE_DIR="."
  PYTHON_VERSION="$LAMBDA_RUNTIME"
else
  # Direct command line usage
  MODULE_DIR="$1"
  PYTHON_VERSION="${2:-python3.13}"  # Default to python3.13 if not provided
fi

# Define paths
FILES_DIR="${MODULE_DIR}/files"
SOURCE_DIR="${MODULE_DIR}/source"
TEMP_DIR="${MODULE_DIR}/files/temp"

# Define zip filename
LAMBDA_ZIP_NAME="lambda_function.zip"
LAMBDA_ZIP_PATH="${FILES_DIR}/${LAMBDA_ZIP_NAME}"

echo "Will create zip file: $LAMBDA_ZIP_NAME"
echo "Absolute path: $LAMBDA_ZIP_PATH"

# Clean all files at the beginning
echo "Cleaning all files and directories..."
if [ -d "$FILES_DIR" ]; then
  rm -rf "$FILES_DIR"/*
  echo "All files have been cleaned."
else
  echo "Files directory does not exist. Creating it..."
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p "$FILES_DIR"
mkdir -p "$TEMP_DIR"

# Create a new directory for the Lambda function
echo "Creating Lambda function directory..."
mkdir -p "$TEMP_DIR/lambda_function"

# Copy all source files to the lambda_function directory
echo "Copying source files..."
cp -r "$SOURCE_DIR"/* "$TEMP_DIR/lambda_function/"

# Create and activate virtual environment with specified Python version
echo "Setting up Python virtual environment using $PYTHON_VERSION..."
cd "$TEMP_DIR/lambda_function"
$PYTHON_VERSION -m venv venv
if [ "$(uname)" = "Darwin" ]; then
  source venv/bin/activate
else
  source venv/bin/activate
fi

# Extract the Python version number for the package path
PYTHON_VERSION_NUM=$(echo $PYTHON_VERSION | grep -o '[0-9]\+\.[0-9]\+')

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create the package directory
echo "Creating package directory..."
mkdir -p package

# Copy all dependencies to the package directory
echo "Copying dependencies..."
cp -r venv/lib/python$PYTHON_VERSION_NUM/site-packages/* package/

# Copy all Lambda function files
echo "Copying Lambda function files..."
cp -r *.py package/

echo "Build process completed successfully!"

# Output JSON result if called from Terraform
if [ -n "$TF_EXTERNAL" ]; then
  echo '{"result": "package_built", "hash": "'"$SOURCE_CODE_HASH"'"}'
fi 