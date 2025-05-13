![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Test Coverage](https://img.shields.io/badge/coverage-85%25-green?style=for-the-badge&logoColor=white)

# Grafana CloudWatch Key Rotator

## Overview

A security-focused automation tool that manages AWS access keys for Grafana CloudWatch data sources. Features include:
- Automated key rotation on a configurable schedule
- Secure key storage and management
- Seamless integration with Grafana CloudWatch data sources
- Zero-downtime key rotation process
- Audit logging for compliance and security tracking


## Deployment

### Installation Steps

1. Ensure you have AWS credentials configured:
   ```bash
   aws configure
   ```

2. Configure your variables in `terraform.auto.tfvars`:
   ```hcl
   aws_region = "us-east-1"
   grafana_url = "https://your-grafana-instance"
   grafana_access_token = "your-grafana-token"
   rotation_period_days = 30
   ```

3. Deploy the infrastructure:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Additional Resources

- [AWS IAM Documentation](https://docs.aws.amazon.com/iam/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)

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
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [template_file.lambda_policy_rotate_iam_keys](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy the resources in | `string` | `"us-east-1"` | no |
| <a name="input_grafana_access_token"></a> [grafana\_access\_token](#input\_grafana\_access\_token) | The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stored in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF\_VAR\_grafana\_access\_token=<your\_token> | `string` | n/a | yes |
| <a name="input_grafana_datasource_name"></a> [grafana\_datasource\_name](#input\_grafana\_datasource\_name) | The name of the Grafana datasource | `string` | `"cw-demo-rotator-access-key"` | no |
| <a name="input_grafana_url"></a> [grafana\_url](#input\_grafana\_url) | The URL of the Grafana instance | `string` | n/a | yes |
| <a name="input_grafana_user_name"></a> [grafana\_user\_name](#input\_grafana\_user\_name) | The name of the Grafana user | `string` | `"grafana-demo-rotator-access-key"` | no |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The runtime of the Lambda function (e.g., python3.13) | `string` | `"python3.13"` | no |
| <a name="input_rotation_period_days"></a> [rotation\_period\_days](#input\_rotation\_period\_days) | Number of days after which access keys should be rotated | `number` | `30` | no |
| <a name="input_schedule_expression_iam_key_rotation"></a> [schedule\_expression\_iam\_key\_rotation](#input\_schedule\_expression\_iam\_key\_rotation) | Schedule expression for the CloudWatch event for the iam key rotation | `string` | `"cron(0 8 * * ? *)"` | no |
<!-- END_TF_DOCS -->
