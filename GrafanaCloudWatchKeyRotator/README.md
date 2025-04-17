# Grafana CloudWatch Key Rotator

## Overview

The Grafana CloudWatch Key Rotator is a security and maintenance solution that automatically rotates IAM access keys used by Grafana to access CloudWatch metrics. This ensures your AWS monitoring infrastructure follows security best practices by regularly rotating credentials without manual intervention.

### Key Features

- **Automated Key Rotation**: Automatically rotates IAM access keys on a configurable schedule
- **Grafana Integration**: Seamlessly updates Grafana data source credentials
- **CloudWatch Monitoring**: Tracks key age and rotation events
- **Terraform Implementation**: Easily deployed and managed with Terraform
- **Secure Key Management**: Uses AWS Secrets Manager and KMS for secure key storage
- **Configurable Rotation Period**: Set custom rotation schedules (default: 30 days)
- **Zero-Downtime Rotation**: Maintains continuous Grafana monitoring during rotation

## Architecture

The Grafana CloudWatch Key Rotator consists of the following components:

1. **Rotator Lambda Function**: A Python-based Lambda function that:
   - Manages IAM access key creation and deletion
   - Updates Grafana data source credentials
   - Stores credentials securely in AWS Secrets Manager
   - Runs on a scheduled basis (configurable via `schedule_expression_iam_key_rotation`)

2. **CloudWatch Event Rule**: Triggers the Rotator Lambda function at regular intervals

3. **AWS Secrets Manager**: Securely stores and manages Grafana API keys and AWS credentials

4. **KMS Key**: Custom KMS key for encryption of sensitive information

5. **IAM User for Grafana**: Dedicated IAM user with CloudWatch read access for Grafana

## Integration Components

The solution is fully integrated with the following components working together:

### 1. IAM User and Permissions
- **Grafana IAM User**:
  - Dedicated user for Grafana CloudWatch access
  - CloudWatchReadOnlyAccess policy
  - Automatic access key rotation

### 2. KMS Encryption
- **Custom Master Key**:
  - Dedicated KMS key for sensitive data encryption
  - Used to encrypt secrets in AWS Secrets Manager
  - Controlled access via KMS policy

### 3. Lambda Rotator
- **Core Functionality**:
  - Automated IAM key creation and deactivation
  - Grafana API integration for data source updates
  - AWS Secrets Manager integration
- **Configuration**:
  - Configurable rotation schedule (default: 60 minutes check)
  - Configurable key age threshold (default: 30 days)
  - Environment variable configuration
- **Monitoring**:
  - CloudWatch logs for debugging
  - Error tracking and reporting
  - Key rotation events

### 4. Grafana Integration
- **Data Source Configuration**:
  - CloudWatch data source automatic updates
  - Seamless credential rotation
  - No monitoring downtime

### Integration Flow
1. **Deployment**:
   - Terraform creates IAM user with initial access keys
   - Rotator Lambda is deployed with necessary permissions
   - Grafana data source is configured with initial credentials

2. **Operation**:
   - Rotator Lambda runs on schedule
   - Checks age of current access keys
   - Creates new keys when rotation is needed
   - Updates Grafana data source credentials
   - Deactivates and eventually deletes old keys

3. **Security**:
   - All sensitive information encrypted with KMS
   - Keys rotated regularly
   - Least privilege principle applied to all components

## Deployment

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd GrafanaCloudWatchKeyRotator
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Configure your variables in `terraform.auto.tfvars`:
   ```hcl
   aws_region = "us-east-1"
   grafana_url = "https://your-grafana-instance"
   grafana_access_token = "your-grafana-token"
   rotation_period_days = 30
   ```

4. Review the configuration:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Monitoring

After deployment, you can monitor your key rotation through:

1. **CloudWatch Logs**:
   - Check the logs of the Rotator Lambda function
   - Monitor for successful rotations and any errors

2. **AWS Secrets Manager**:
   - View the rotation history of your secrets
   - Verify the last rotation date

3. **IAM Console**:
   - Check the access keys for the Grafana IAM user
   - Verify creation and deletion timestamps

## Best Practices

1. **Rotation Period**:
   - Set an appropriate rotation period based on your security requirements
   - Industry standard is 30-90 days

2. **Grafana API Token**:
   - Store your Grafana API token securely
   - Consider rotating this token regularly as well

3. **Monitoring**:
   - Set up CloudWatch alarms for rotation failures
   - Monitor for unexpected key creation or deletion

4. **Security**:
   - Use IAM roles with least privilege
   - Keep the KMS key access restricted
   - Monitor CloudWatch logs for suspicious activity

## Troubleshooting

Common issues and solutions:

1. **Failed Rotations**:
   - Check CloudWatch logs for detailed error messages
   - Verify Grafana API token validity
   - Ensure Lambda function has necessary permissions

2. **Grafana Connection Issues**:
   - Verify Grafana URL and access token
   - Check CloudWatch data source configuration
   - Ensure proper network connectivity between Lambda and Grafana

3. **Permission Issues**:
   - Verify IAM roles and policies
   - Check KMS key permissions
   - Ensure Lambda execution role has necessary permissions

## Support

For issues and feature requests, please:
1. Check the existing documentation
2. Review CloudWatch logs
3. Open an issue in the repository

## Additional Resources

- [AWS IAM Documentation](https://docs.aws.amazon.com/iam/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.11 |
| <a name="requirement_archive"></a> [archive](#requirement\_archive) | ~> 2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.59.0 |
| <a name="requirement_external"></a> [external](#requirement\_external) | ~> 2.2 |
| <a name="requirement_grafana"></a> [grafana](#requirement\_grafana) | ~> 3.22.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | ~> 3.2 |
| <a name="requirement_template"></a> [template](#requirement\_template) | ~> 2 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_rotate_iam_keys"></a> [lambda\_rotate\_iam\_keys](#module\_lambda\_rotate\_iam\_keys) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | v6.4.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.iam_key_rotation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.rotate_iam_keys_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_user.grafana](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user_policy_attachment.cloudwatch_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [aws_kms_key.cmk](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_secretsmanager_secret.grafana_api_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.grafana_api_key_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [grafana_data_source.cloudwatch](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/data_source) | resource |
| [archive_file.lambda_zip](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [external_external.build_lambda_package](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |
| [template_file.lambda_policy_rotate_iam_keys](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy the resources in | `string` | `"us-east-1"` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment to deploy the resources in | `string` | `"prod"` | no |
| <a name="input_grafana_access_token"></a> [grafana\_access\_token](#input\_grafana\_access\_token) | The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stored in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF\_VAR\_grafana\_access\_token=<your\_token> | `string` | n/a | yes |
| <a name="input_grafana_datasource_name"></a> [grafana\_datasource\_name](#input\_grafana\_datasource\_name) | The name of the Grafana datasource | `string` | `"cw"` | no |
| <a name="input_grafana_url"></a> [grafana\_url](#input\_grafana\_url) | The URL of the Grafana instance | `string` | n/a | yes |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The runtime of the Lambda function (e.g., python3.13) | `string` | `"python3.13"` | no |
| <a name="input_rotation_period_days"></a> [rotation\_period\_days](#input\_rotation\_period\_days) | Number of days after which access keys should be rotated | `number` | `30` | no |
| <a name="input_schedule_expression_iam_key_rotation"></a> [schedule\_expression\_iam\_key\_rotation](#input\_schedule\_expression\_iam\_key\_rotation) | Schedule expression for the CloudWatch event for the iam key rotation | `string` | `"cron(0 8 * * ? *)"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->