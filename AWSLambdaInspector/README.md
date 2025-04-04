# AWS Lambda Inspector

### Overview

The AWS Lambda Inspector is a Terraform module that deploys a Lambda function to inspect other Lambda functions in your AWS account. It collects metadata tags from each function and publishes custom metrics to Amazon CloudWatch. These metrics help in tracking the deployment environment, service, stack, and Terraform version associated with each Lambda function.

### Prerequisites

Ensure your Lambda functions have the following tags:
- `AppVersion`: The application version, such as the Maven version for Java projects.
- `TerraformVersion`: The terraform version used to deploy the lambda. It's the stack tag.

### Project Structure

Below is a visual representation of the relationship between different components:

```
Account
└── Environment
    ├── Service 1
    │   ├── Stack 1
    │   │   ├── Lambda 1
    │   │   └── Lambda 2
    │   └── Stack 2
    │       ├── Lambda 3
    │       └── Lambda 4
    └── Service 2
        ├── Stack 3
        │   ├── Lambda 5
        │   └── Lambda 6
        └── Stack 4
            ├── Lambda 7
            └── Lambda 8
```

This diagram provides a hierarchical view of how accounts, environments, services, stacks, and Lambdas are organized.

### Functionality

The Lambda function performs the following tasks:

1. **List Lambda Functions**: It uses the AWS SDK for Python (Boto3) to list all Lambda functions in the account.

2. **Retrieve Tags**: For each function, it retrieves tags such as `AppVersion`, `Stack`, `Service`, `Environment`, and `TerraformVersion`.

3. **Publish Metrics**: 
   - It publishes a `lambdaTag` metric to CloudWatch for each function, including dimensions for `Env`, `Service`, `Stack`, `FunctionName`, and `AppVersion`.
   - It aggregates services and publishes a `terraformTag` metric with dimensions for `Env`, `Service`, `Stack`, and `TerraformVersion`.

### Deployment

To deploy the AWS Lambda Inspector, follow these steps:

1. Ensure you have the required versions of Terraform and AWS provider as specified in the `terraform` folder.

2. Clone the repository and navigate to the `terraform` directory.

3. Initialize the Terraform configuration:
   ```bash
   terraform init
   ```

4. Apply the Terraform configuration to deploy the stack:
   ```bash
   terraform apply
   ```

5. Confirm the deployment by checking the CloudWatch metrics for the `lambdaTag` and `terraformTag`.

### Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)

This setup will enable you to monitor and manage your AWS Lambda functions effectively using the custom metrics published to CloudWatch.
 