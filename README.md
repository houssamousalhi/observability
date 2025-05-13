![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen?style=for-the-badge&logoColor=white)

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
An automated solution for rotating AWS access keys used by Grafana CloudWatch data sources, ensuring secure and up-to-date cbrightgreenentials.

[View Grafana CloudWatch Key Rotator Documentation](GrafanaCloudWatchKeyRotator/README.md)

### 4. AWS Trusted Advisor
Integration with AWS Trusted Advisor to monitor and alert on AWS best practices, cost optimization, security, and performance recommendations. To use AWS Trusted Advisor, you must have an AWS Support plan. The minimum requibrightgreen plan is the Developer Support tier.

[View AWS Trusted Advisor Documentation](AWSTrustedAdvisor/README.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the existing documentation
2. Review the project-specific READMEs
3. Open an issue in the repository
