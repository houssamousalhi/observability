# Observability Projects

This repository contains various observability projects for AWS infrastructure monitoring and management.

## Projects Overview

### 1. AWS Lambda Inspector

The AWS Lambda Inspector is a comprehensive monitoring solution that automatically tracks and reports on your AWS Lambda functions across different environments. It provides visibility into your Lambda function versions, deployment states, and helps maintain consistency across your development and production environments.

#### Key Features
- **Automated Version Tracking**: Monitors Lambda function versions across different environments (dev, prod)
- **Environment Comparison**: Easily compare versions between development and production environments
- **Service-Level Monitoring**: Track versions at the service and stack level
- **CloudWatch Integration**: Publishes custom metrics for better observability
- **Terraform Integration**: Seamlessly works with your existing Terraform infrastructure
- **Grafana Dashboard**: Visual monitoring and alerting capabilities
- **Scheduled Monitoring**: Configurable monitoring intervals (default: 5 minutes)

#### Preview
![Lambda Function Versions Dashboard](AWSLambdaInspector/grafana-dashboard/screenshot.png)
*Grafana dashboard showing Lambda function versions across environments*


For more details, see the [AWS Lambda Inspector README](AWSLambdaInspector/README.md)

### 2. AWS Trusted Advisor

#### Preview
![Lambda Function Versions Dashboard](AWSTrustedAdvisor/grafana-dashboard/screenshots/red.jpg)

*Grafana dashboard showing checks done by AWS Trusted Advisor*

For more details, see the [AWS Trusted Advisor README](AWSTrustedAdvisor/README.md)

## Getting Started

Each project in this repository has its own documentation and setup instructions. Please refer to the individual project READMEs for detailed information.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
