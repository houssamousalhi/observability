![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Test Coverage](https://img.shields.io/badge/coverage-94.62%25-brightgreen)
# AWS Observability Solutions

This repository contains a collection of AWS observability solutions that help monitor, analyze, and maintain your AWS infrastructure. Each solution is designed to work independently or together to provide comprehensive observability across your AWS environment.

## Projects

### 1. AWS CloudWatch Alarms
A comprehensive monitoring and alerting system for AWS resources using CloudWatch metrics. Provides automated monitoring, alerting.

[View AWS CloudWatch Alarms Documentation](AWSCloudWatchAlarm/README.md)

### 2. AWS Lambda Inspector
The AWS Lambda Inspector is a comprehensive monitoring solution that automatically tracks and reports on your AWS Lambda functions across different environments. It provides visibility into your Lambda function versions, deployment states, and helps maintain consistency across your development and production environments.

To ensure comprehensive version tracking, it's essential to monitor both the Infrastructure as Code (IAC) version and the Application version. The IAC version captures infrastructure-related changes such as environment variables, IAM permissions, and other AWS resource configurations, while the Application version tracks the actual code and package changes.

[View AWS Lambda Inspector Documentation](AWSLambdaInspector/README.md)

### 3. Grafana CloudWatch Key Rotator
An automated solution for rotating AWS access keys used by Grafana CloudWatch data sources, ensuring secure and up-to-date credentials.

[View Grafana CloudWatch Key Rotator Documentation](GrafanaCloudWatchKeyRotator/README.md)

### 4. AWS Trusted Advisor
Integration with AWS Trusted Advisor to monitor and alert on AWS best practices, cost optimization, security, and performance recommendations. To use AWS Trusted Advisor, you must have an AWS Support plan. The minimum required plan is the Developer Support tier.

[View AWS Trusted Advisor Documentation](AWSTrustedAdvisor/README.md)

## Common Features

All solutions in this repository share the following features:

- **Terraform Integration**: Infrastructure as Code using Terraform
- **Grafana Integration**: Visual monitoring and alerting capabilities
- **Security Best Practices**: IAM roles with least privilege
- **Cost Optimization**: Efficient resource utilization
- **Automated Deployment**: Streamlined setup and configuration

## Prerequisites

- AWS Account with appropriate permissions
- Terraform (>= 1.0.11)
- AWS CLI configured
- Grafana instance (self-hosted or cloud)
- Python 3.8 or higher (for Lambda functions)

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd observability
   ```

2. Choose the solution you want to deploy and navigate to its directory:
   ```bash
   cd <solution-directory>
   ```

3. Follow the specific setup instructions in each solution's README.md file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the existing documentation
2. Review the project-specific READMEs
3. Open an issue in the repository

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
