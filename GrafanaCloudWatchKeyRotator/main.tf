module "lambda_rotate_iam_keys" {
  source                            = "git::https://gitlab.softfactory-accor.net/rbac/cd/it4it/terraform-modules/community/terraform-aws-lambda.git?ref=v6.4.0"
  function_name                     = "lbd-${var.environment}-grafana-cloudwatch-key-rotator"
  description                       = "rotate grafana cloudwatch key"
  handler                           = "grafana_cloudwatch_key_rotator.lambda_handler"
  runtime                           = "python3.13"
  memory_size                       = 160
  timeout                           = 30
  create_package                    = false
  local_existing_package            = data.archive_file.lambda_zip.output_path
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  number_of_policy_jsons            = 1
  policy_jsons                      = [data.template_file.lambda_policy_rotate_iam_keys.rendered]
  policies                          = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  cloudwatch_logs_retention_in_days = 30
  create_lambda_function_url        = false
  environment_variables = {
    IAM_USERNAME            = aws_iam_user.grafana.name
    GRAFANA_API_KEY_PATH    = "grafana/apikey"
    GRAFANA_URL             = var.grafana_url
    GRAFANA_DATASOURCE_NAME = var.grafana_datasource_name
    ROTATION_PERIOD         = var.rotation_period_days
  }
  allowed_triggers = {
    DailyRotation = {
      principal    = "events.amazonaws.com"
      source_arn   = aws_cloudwatch_event_rule.iam_key_rotation.arn
      statement_id = "AllowExecutionFromCloudWatch"
    }
  }
}

# CloudWatch Event Rules
resource "aws_cloudwatch_event_rule" "iam_key_rotation" {
  name                = "iam_key_rotation_schedule"
  description         = "Schedule for IAM access key rotation"
  schedule_expression = var.schedule_expression_iam_key_rotation
}

# CloudWatch Event Targets
resource "aws_cloudwatch_event_target" "rotate_iam_keys_target" {
  rule      = aws_cloudwatch_event_rule.iam_key_rotation.name
  target_id = "SendToRotateIamKeys"
  arn       = module.lambda_rotate_iam_keys.lambda_function_arn
}

# IAM Policies
data "template_file" "lambda_policy_rotate_iam_keys" {
  template = file("${path.module}/iam_policy_rotate_iam_keys.json.tpl")
  vars = {
    aws_region = var.aws_region
    account_id = data.aws_caller_identity.current.account_id
    kms_key_id = aws_kms_key.cmk.key_id
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "./files/grafana_cloudwatch_key_rotator.zip"
  source_dir  = "./files/temp/lambda_function/package"
  depends_on  = [null_resource.build_lambda_package]
}


resource "null_resource" "build_lambda_package" {
  triggers = {
    requirements_hash = filesha256("${path.module}/source/requirements.txt")
    source_hash       = filesha256("${path.module}/source/grafana_cloudwatch_key_rotator.py")
  }

  provisioner "local-exec" {
    command     = <<EOT
      set -e  # Exit on any error
      
      # Define paths
      MODULE_DIR="${path.module}"
      FILES_DIR="${path.module}/files"
      SOURCE_DIR="${path.module}/source"
      TEMP_DIR="${path.module}/files/temp"

      # Create necessary directories
      echo "Creating directories..."
      mkdir -p "$FILES_DIR"
      mkdir -p "$TEMP_DIR"
      
      # Clean up any existing files
      echo "Cleaning up existing files..."
      rm -rf "$TEMP_DIR"
      rm -f "$ZIP_FILE"
      
      # Create a new directory for the Lambda function
      echo "Creating Lambda function directory..."
      mkdir -p "$TEMP_DIR/lambda_function"
      
      # Copy source files to the lambda_function directory
      echo "Copying source files..."
      cp "$SOURCE_DIR/grafana_cloudwatch_key_rotator.py" "$TEMP_DIR/lambda_function/"
      cp "$SOURCE_DIR/requirements.txt" "$TEMP_DIR/lambda_function/"
      
      # Create and activate virtual environment with Python 3.13
      echo "Setting up Python virtual environment..."
      cd "$TEMP_DIR/lambda_function"
      python3.13 -m venv venv
      if [ "$(uname)" = "Darwin" ]; then
        source venv/bin/activate
      else
        source venv/bin/activate
      fi
      
      # Upgrade pip and install dependencies
      echo "Installing dependencies..."
      pip install --upgrade pip
      pip install -r requirements.txt
      
      # Create the package directory
      echo "Creating package directory..."
      mkdir -p package
      
      # Copy all dependencies to the package directory
      echo "Copying dependencies..."
      cp -r venv/lib/python3.13/site-packages/* package/
      
      # Copy the Lambda function
      echo "Copying Lambda function..."
      cp grafana_cloudwatch_key_rotator.py package/
 
      echo "Build process completed successfully!"
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}