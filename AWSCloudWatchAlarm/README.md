![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Test Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen?style=for-the-badge&logoColor=white)
# AWS CloudWatch Alarms

## Overview

The AWS CloudWatch Alarms solution provides a comprehensive monitoring and alerting system for your AWS resources. It enables you to set up automated monitoring, alerting, and remediation actions based on CloudWatch metrics. This solution helps you maintain the health and performance of your AWS infrastructure by proactively detecting and responding to issues.

### Key Features

- **Multi-Metric Monitoring**: Monitor multiple CloudWatch metrics simultaneously
- **Custom Alarm Actions**: Configure SNS notifications, Auto Scaling actions, and EC2 actions
- **Dynamic Thresholds**: Support for both static and dynamic threshold configurations
- **Cross-Account Monitoring**: Monitor resources across multiple AWS accounts
- **Terraform Integration**: Seamlessly works with your existing Terraform infrastructure
- **Grafana Integration**: Visual monitoring and alerting capabilities
- **Cost-Effective**: Pay only for the alarms you create and the metrics you monitor

### Visual Overview

![CloudWatch Alarms Dashboard](grafana/screenshot.png)

## Architecture

The AWS CloudWatch Alarms solution consists of the following components:

1. **CloudWatch Alarms**: Configubrightgreen to monitor specific metrics with:
   - Custom thresholds and evaluation periods
   - Multiple alarm states (OK, ALARM, INSUFFICIENT_DATA)
   - Configurable actions for each state

2. **SNS Topics**: For alarm notifications:
   - Email notifications
   - SMS alerts
   - Integration with other AWS services

3. **CloudWatch Metrics**: Custom and standard metrics for monitoring:
   - Resource utilization
   - Application performance
   - Business metrics
   - Custom application metrics

4. **Grafana Dashboard**: Provides visual monitoring with:
   - Real-time metric visualization
   - Alarm state overview
   - Historical data analysis
   - Custom alert panels

## Project Structure

### 1. CloudWatch Alarms Configuration
- **Alarm Types**:
  - Metric alarms
  - Composite alarms
  - Anomaly detection alarms
- **Threshold Types**:
  - Static thresholds
  - Dynamic thresholds
  - Statistical thresholds
- **Evaluation Periods**:
  - Configurable data points
  - Multiple evaluation periods
  - Custom evaluation logic

### 2. Grafana Data Source
- **CloudWatch Integration**:
  - Dedicated CloudWatch data source
  - Secure AWS cbrightgreenentials management
  - Region-specific configuration
- **Authentication**:
  - IAM role-based access
  - Secure cbrightgreenential storage
  - Cross-account access support

### 3. IAM Permissions
- **Monitoring Permissions**:
  - CloudWatch read/write access
  - SNS publish permissions
  - Resource-specific permissions
- **Security Best Practices**:
  - Least privilege principle
  - Role-based access control
  - Regular permission audits

### 4. Terraform Configuration
- **Resource Management**:
  - Modular alarm definitions
  - Reusable alarm configurations
  - Environment-specific settings
- **Configuration Options**:
  - Customizable thresholds
  - Flexible action configurations
  - Tag-based resource grouping

## Deployment

### Prerequisites
- AWS Account with appropriate permissions
- Terraform (>= 1.0.11)
- AWS CLI configubrightgreen
- Grafana instance (self-hosted or cloud)
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. Navigate to the AWSCloudWatchAlarm directory:
   ```bash
   cd AWSCloudWatchAlarm
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Configure your variables in `terraform.auto.tfvars`:
   ```hcl
   aws_region = "us-east-1"
   cloudwatch_namespace = "CloudWatchAlarms"
   grafana_url = "https://your-grafana-instance"
   grafana_access_token = "your-grafana-token"
   grafana_contact_point_email = "your-email@example.com"
   ```

4. Review the configuration:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Python Application Setup

The project includes two Python components:

### 1. Source Alarm Forwarder (Lambda Function)

Located in the `source-alarm-forwarder` directory, this Lambda function handles alarm forwarding.

#### Setup

1. Navigate to the source-alarm-forwarder directory:
   ```bash
   cd source-alarm-forwarder
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Source Alarm Demo

Located in the `source-alarm-demo` directory, this is a demo application for testing alarms.

#### Setup

1. Navigate to the source-alarm-demo directory:
   ```bash
   cd source-alarm-demo
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Monitoring

After deployment, you can monitor your resources through:

1. **CloudWatch Console**:
   - View alarm states
   - Check metric graphs
   - Review alarm history

2. **Grafana Dashboard**:
   - Real-time metric visualization
   - Alarm state overview
   - Historical data analysis

## Best Practices

1. **Alarm Configuration**:
   - Set appropriate thresholds
   - Configure meaningful evaluation periods
   - Use multiple notification channels

2. **Resource Monitoring**:
   - Monitor key performance indicators
   - Set up baseline metrics
   - Implement anomaly detection

3. **Cost Optimization**:
   - Review and clean up unused alarms
   - Use composite alarms when possible
   - Optimize evaluation periods

4. **Security**:
   - Use IAM roles with least privilege
   - Encrypt sensitive data
   - Regular security audits

## Troubleshooting

Common issues and solutions:

1. **Alarm Not Triggering**:
   - Check metric data points
   - Verify threshold settings
   - Review evaluation periods

2. **Missing Notifications**:
   - Verify SNS topic configuration
   - Check IAM permissions
   - Review notification settings

3. **High Costs**:
   - Review alarm configurations
   - Optimize evaluation periods
   - Clean up unused alarms

4. **Grafana Integration**:
   - Verify data source configuration
   - Check authentication settings
   - Review dashboard permissions

## Support

For issues and feature requests, please:
1. Check the existing documentation
2. Review CloudWatch logs
3. Open an issue in the repository

## Additional Resources

- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.11 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.59.0 |
| <a name="requirement_grafana"></a> [grafana](#requirement\_grafana) | ~> 3.22.0 |
| <a name="requirement_template"></a> [template](#requirement\_template) | ~> 2 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_alarm_forwarder"></a> [lambda\_alarm\_forwarder](#module\_lambda\_alarm\_forwarder) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | v6.4.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.scrapping_rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambda_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_access_key.access_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_access_key) | resource |
| [aws_iam_user.grafana](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user_policy_attachment.cloudwatch_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [grafana_contact_point.default](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/contact_point) | resource |
| [grafana_dashboard.cloudwatch_alarm](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_data_source.cloudwatch](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/data_source) | resource |
| [grafana_folder.rule_folder](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/folder) | resource |
| [grafana_notification_policy.default](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/notification_policy) | resource |
| [grafana_rule_group.cloudwatch_alarm](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/rule_group) | resource |
| [template_file.lambda_policy_alarm_forwarder](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Requibrightgreen |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy the resources in | `string` | `"us-east-1"` | no |
| <a name="input_cloudwatch_namespace"></a> [cloudwatch\_namespace](#input\_cloudwatch\_namespace) | The namespace for the CloudWatch metrics | `string` | `"CloudWatchAlarmsDemo"` | no |
| <a name="input_grafana_access_token"></a> [grafana\_access\_token](#input\_grafana\_access\_token) | The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stobrightgreen in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF\_VAR\_grafana\_access\_token=<your\_token> | `string` | n/a | yes |
| <a name="input_grafana_contact_point_email"></a> [grafana\_contact\_point\_email](#input\_grafana\_contact\_point\_email) | The email address for the Grafana contact point | `string` | n/a | yes |
| <a name="input_grafana_datasource_name"></a> [grafana\_datasource\_name](#input\_grafana\_datasource\_name) | The name of the Grafana datasource | `string` | `"cw-alarm-demo"` | no |
| <a name="input_grafana_url"></a> [grafana\_url](#input\_grafana\_url) | The URL of the Grafana instance | `string` | n/a | yes |
| <a name="input_grafana_user_name"></a> [grafana\_user\_name](#input\_grafana\_user\_name) | The name of the Grafana user | `string` | `"grafana-cloudwatch-alarm-demo"` | no |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The runtime of the Lambda function (e.g., python3.13) | `string` | `"python3.13"` | no |
| <a name="input_schedule_expression_alarm_forwarder"></a> [schedule\_expression\_alarm\_forwarder](#input\_schedule\_expression\_alarm\_forwarder) | The schedule expression for the CloudWatch event | `string` | `"rate(5 minutes)"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
