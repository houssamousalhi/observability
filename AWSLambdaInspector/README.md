# AWS Lambda Inspector

## Overview

The AWS Lambda Inspector is a comprehensive monitoring solution that automatically tracks and reports on your AWS Lambda functions across different environments. It provides visibility into your Lambda function versions, deployment states, and helps maintain consistency across your development and production environments.

### Key Features

- **Automated Version Tracking**: Monitors Lambda function versions across different environments (dev, prod)
- **Environment Comparison**: Easily compare versions between development and production environments
- **Service-Level Monitoring**: Track versions at the service and stack level
- **CloudWatch Integration**: Publishes custom metrics for better observability
- **Terraform Integration**: Seamlessly works with your existing Terraform infrastructure
- **Grafana Dashboard**: Visual monitoring and alerting capabilities
- **Scheduled Monitoring**: Configurable monitoring intervals (default: 5 minutes)

### Visual Overview
 
![Lambda Function Versions Dashboard](grafana-dashboard/screenshot.png) 

## Architecture

The AWS Lambda Inspector consists of the following components:

1. **Inspector Lambda Function**: A Python-based Lambda function that:
   - Lists all Lambda functions in your AWS account
   - Retrieves tags and version information
   - Publishes metrics to CloudWatch
   - Runs on a scheduled basis (configurable via `schedule_expression`)

2. **CloudWatch Event Rule**: Triggers the Inspector Lambda function at regular intervals

3. **CloudWatch Metrics**: Custom metrics published for monitoring:
   - `lambdaTag`: Function-level metrics with dimensions for environment, service, stack, and version
   - `terraformTag`: Stack-level metrics for Terraform version tracking

4. **Grafana Dashboard**: Provides visual monitoring with:
   - Version comparison across environments
   - Service-level overview
   - Stack-level monitoring

## Integration Components

The solution is fully integrated with the following components working together:

### 1. Example Stack with Multiple Levels
- **Hierarchical Structure**:
  - Environment (dev/prod) → Stack → Service → Lambda Function
  - Each level is configurable through `var.lambda_versions`
- **Tagging System**:
  - `Environment`: Deployment environment (dev/prod)
  - `AppVersion`: Application version
  - `Stack`: Stack identifier
  - `Service`: Service name
  - `TerraformVersion`: Terraform version used for deployment

### 2. Grafana Data Source
- **CloudWatch Integration**:
  - Dedicated CloudWatch data source in Grafana
  - Secure AWS credentials management
  - Region-specific configuration
- **Authentication**:
  - Uses IAM user with CloudWatchReadOnlyAccess
  - Secure storage of AWS access keys
  - Automatic key rotation support

### 3. IAM User and Permissions
- **Grafana IAM User**:
  - Dedicated user for Grafana CloudWatch access
  - CloudWatchReadOnlyAccess policy
  - Secure access key management
- **Lambda Inspector Permissions**:
  - Custom IAM policy for Lambda inspection
  - Permission to list and read Lambda functions
  - Permission to publish CloudWatch metrics

### 4. Lambda Inspector
- **Core Functionality**:
  - Automated Lambda function discovery
  - Tag collection and processing
  - CloudWatch metrics publishing
- **Configuration**:
  - Configurable schedule (default: 5 minutes)
  - Custom CloudWatch namespace
  - Environment variable configuration
- **Monitoring**:
  - CloudWatch logs for debugging
  - Error tracking and reporting
  - Performance metrics

### 5. Grafana Dashboard
- **Pre-configured Visualizations**:
  - Version comparison across environments
  - Service-level overview
  - Stack-level monitoring
  - Tag-based filtering
- **Features**:
  - Real-time metric updates
  - Customizable panels
  - Alert configuration support

### Integration Flow
1. **Deployment**:
   - Terraform creates example Lambda functions with proper tags
   - Inspector Lambda is deployed with necessary permissions
   - Grafana data source and dashboard are configured

2. **Operation**:
   - Inspector Lambda runs on schedule
   - Collects tag information from all Lambda functions
   - Publishes metrics to CloudWatch
   - Grafana pulls metrics through data source
   - Dashboard visualizes the data

3. **Monitoring**:
   - Version differences are highlighted
   - Environment comparisons are available
   - Service and stack-level views
   - Alerting on version mismatches

## Deployment

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AWSLambdaInspector/terraform
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Configure your variables in `terraform.auto.tfvars`:
   ```hcl
   aws_region = "us-east-1"
   cloudwatch_namespace = "LambdaInspect"
   grafana_url = "https://your-grafana-instance"
   grafana_access_token = "your-grafana-token"
   schedule_expression = "rate(5 minutes)"
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

After deployment, you can monitor your Lambda functions through:

1. **CloudWatch Metrics**:
   - Navigate to CloudWatch > Metrics
   - Look for custom namespace containing `lambdaTag` and `terraformTag` metrics

2. **CloudWatch Logs**:
   - Check the logs of the Inspector Lambda function
   - Monitor for any errors or version mismatches

3. **Grafana Dashboard**:
   - Access the pre-configured dashboard
   - Monitor version differences across environments
   - Set up alerts for version mismatches

## Best Practices

1. **Version Naming**:
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Keep dev versions higher than prod versions
   - Document version changes in your release notes

2. **Tag Management**:
   - Ensure all Lambda functions have required tags
   - Keep tags consistent across environments
   - Use meaningful service and stack names

3. **Monitoring**:
   - Set up CloudWatch alarms for version mismatches
   - Monitor deployment frequency
   - Track version drift between environments

4. **Security**:
   - Use IAM roles with least privilege
   - Rotate Grafana access tokens regularly
   - Monitor CloudWatch logs for suspicious activity

## Troubleshooting

Common issues and solutions:

1. **Missing Tags**:
   - Ensure all Lambda functions have the required tags
   - Use AWS CLI to verify tags: `aws lambda list-tags --resource <function-arn>`

2. **Version Mismatches**:
   - Check CloudWatch logs for detailed error messages
   - Verify version numbers in variables.tf
   - Ensure dev versions are higher than prod versions

3. **Permission Issues**:
   - Verify IAM roles and policies
   - Check CloudWatch permissions
   - Ensure Lambda execution role has necessary permissions

4. **Grafana Integration**:
   - Verify Grafana URL and access token
   - Check CloudWatch data source configuration
   - Ensure proper permissions for Grafana IAM user

## Support

For issues and feature requests, please:
1. Check the existing documentation
2. Review CloudWatch logs
3. Open an issue in the repository

## Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.11 |
| <a name="requirement_archive"></a> [archive](#requirement\_archive) | ~> 2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.59.0 |
| <a name="requirement_grafana"></a> [grafana](#requirement\_grafana) | ~> 3.22.0 |
| <a name="requirement_template"></a> [template](#requirement\_template) | ~> 2 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_app_inspector"></a> [lambda\_app\_inspector](#module\_lambda\_app\_inspector) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | v6.4.0 |
| <a name="module_lambda_example"></a> [lambda\_example](#module\_lambda\_example) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | v6.4.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.scrapping_rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambda_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_access_key.access_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_access_key) | resource |
| [aws_iam_user.grafana](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user_policy_attachment.cloudwatch_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [grafana_dashboard.lambda_inspector](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_data_source.cloudwatch](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/data_source) | resource |
| [archive_file.app-inspector](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.example](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [template_file.lambda_policy_app_inspector](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy the resources in | `string` | `"us-east-1"` | no |
| <a name="input_cloudwatch_namespace"></a> [cloudwatch\_namespace](#input\_cloudwatch\_namespace) | The namespace for the CloudWatch metrics | `string` | `"LambdaInspect"` | no |
| <a name="input_grafana_access_token"></a> [grafana\_access\_token](#input\_grafana\_access\_token) | The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stored in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF\_VAR\_grafana\_access\_token=<your\_token> | `string` | n/a | yes |
| <a name="input_grafana_url"></a> [grafana\_url](#input\_grafana\_url) | The URL of the Grafana instance | `string` | n/a | yes |
| <a name="input_lambda_versions"></a> [lambda\_versions](#input\_lambda\_versions) | Map of environment, service, stack, and lambda function versions | `map(map(map(map(map(string)))))` | <pre>{<br/>  "dev": {<br/>    "primary": {<br/>      "backend": {<br/>        "consumer": {<br/>          "TerraformVersion": "1.4.0-RC5",<br/>          "version": "2.4.1"<br/>        },<br/>        "producer": {<br/>          "TerraformVersion": "1.4.0-RC6",<br/>          "version": "1.1.1"<br/>        }<br/>      },<br/>      "frontend": {<br/>        "auth": {<br/>          "TerraformVersion": "1.4.0-SNAPSHOT",<br/>          "version": "1.2.0"<br/>        },<br/>        "cache": {<br/>          "TerraformVersion": "1.4.0-SNAPSHOT",<br/>          "version": "2.4.0"<br/>        }<br/>      }<br/>    }<br/>  },<br/>  "prod": {<br/>    "next": {<br/>      "backend": {<br/>        "consumer": {<br/>          "TerraformVersion": "1.4.0-RC5",<br/>          "version": "2.4.1"<br/>        },<br/>        "producer": {<br/>          "TerraformVersion": "1.4.0-RC5",<br/>          "version": "1.1.1"<br/>        }<br/>      },<br/>      "frontend": {<br/>        "auth": {<br/>          "TerraformVersion": "1.3.0-RELEASE",<br/>          "version": "1.2.0"<br/>        },<br/>        "cache": {<br/>          "TerraformVersion": "1.3.0-RELEASE",<br/>          "version": "2.4.0"<br/>        }<br/>      }<br/>    },<br/>    "primary": {<br/>      "backend": {<br/>        "consumer": {<br/>          "TerraformVersion": "1.4.0-RELEASE",<br/>          "version": "2.5.0"<br/>        },<br/>        "producer": {<br/>          "TerraformVersion": "1.4.0-RELEASE",<br/>          "version": "1.2.0"<br/>        }<br/>      },<br/>      "frontend": {<br/>        "auth": {<br/>          "TerraformVersion": "1.3.0-RELEASE",<br/>          "version": "1.2.0"<br/>        },<br/>        "cache": {<br/>          "TerraformVersion": "1.3.0-RELEASE",<br/>          "version": "2.4.0"<br/>        }<br/>      }<br/>    }<br/>  }<br/>}</pre> | no |
| <a name="input_schedule_expression"></a> [schedule\_expression](#input\_schedule\_expression) | The schedule expression for the CloudWatch event | `string` | `"rate(5 minutes)"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->