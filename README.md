![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Test Coverage](https://img.shields.io/badge/coverage-88%25-green?style=for-the-badge&logoColor=white)

| Hook | Status |
|------|--------|
| terraform_fmt | ![terraform_fmt](https://img.shields.io/badge/terraform_fmt-pending-lightgrey) |
| terraform_validate | ![terraform_validate](https://img.shields.io/badge/terraform_validate-pending-lightgrey) |
| terraform_docs | ![terraform_docs](https://img.shields.io/badge/terraform_docs-pending-lightgrey) |
| terraform_tflint | ![terraform_tflint](https://img.shields.io/badge/terraform_tflint-pending-lightgrey) |
| terraform_trivy | ![terraform_trivy](https://img.shields.io/badge/terraform_trivy-pending-lightgrey) |
| terraform_checkov | ![terraform_checkov](https://img.shields.io/badge/terraform_checkov-pending-lightgrey) |
| black | ![black](https://img.shields.io/badge/black-pending-lightgrey) |
| pytest | ![pytest](https://img.shields.io/badge/pytest-pending-lightgrey) |



# AWS Observability Solutions

This repository contains a collection of AWS observability solutions that help monitor, analyze, and maintain your AWS infrastructure. Each solution is designed to work independently or together to provide comprehensive observability across your AWS environment.

## Projects

### 1. AWS CloudWatch Alarms
A comprehensive AWS observability solution that centralizes all CloudWatch alarms in Grafana. This project provides:
- Automated forwarding of CloudWatch alarms to Grafana
- A unified dashboard for monitoring alarms across all AWS services
- Customizable alerting rules and notification channels
- Real-time visibility into your AWS infrastructure health
- Multi-channel notifications through:
  - Email alerts with detailed HTML formatting
  - Slack integration for team collaboration
  - Google Chat integration for workspace communication

[View Documentation](AWSCloudWatchAlarm/README.md)

### 2. AWS Lambda Inspector
A sophisticated monitoring solution that provides complete visibility into your AWS Lambda functions lifecycle. Key features include:
- Automated tracking of both Infrastructure as Code (IAC) and Application versions
- Comprehensive deployment history and change tracking

[View Documentation](AWSLambdaInspector/README.md)

### 3. Grafana CloudWatch Key Rotator
A security-focused automation tool that manages AWS access keys for Grafana CloudWatch data sources. Features include:
- Automated key rotation on a configurable schedule
- Secure key storage and management
- Seamless integration with Grafana CloudWatch data sources
- Zero-downtime key rotation process
- Audit logging for compliance and security tracking

[View Documentation](GrafanaCloudWatchKeyRotator/README.md)

### 4. AWS Trusted Advisor
A ready-to-use Grafana dashboard that visualizes AWS Trusted Advisor check results. Note: This solution requires an AWS Trusted Advisor subscription with at least the Developer Support tier to function. The dashboard provides:
- Real-time visualization of Trusted Advisor check results
- Monitoring of critical (green) and warning (yellow) checks

[View Documentation](AWSTrustedAdvisor/README.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the existing documentation
2. Review the project-specific READMEs
3. Open an issue in the repository
