import boto3
import os
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

CLOUDWATCH_NAMESPACE = os.environ.get("CLOUDWATCH_NAMESPACE")


@dataclass
class LambdaFunction:
    name: str
    arn: str
    tags: Dict[str, str]


@dataclass(frozen=True)
class ServiceInfo:
    env: str
    service: str
    stack: str
    terraform_version: str


class LambdaInspector:
    def __init__(self):
        self.lambda_client = boto3.client("lambda")
        self.cloudwatch_client = boto3.client("cloudwatch")

    def get_all_functions(self) -> List[LambdaFunction]:
        functions = []
        paginator = self.lambda_client.get_paginator("list_functions")

        for page in paginator.paginate():
            for function in page["Functions"]:
                try:
                    tags = self.lambda_client.list_tags(
                        Resource=function["FunctionArn"]
                    ).get("Tags", {})
                    functions.append(
                        LambdaFunction(
                            name=function["FunctionName"],
                            arn=function["FunctionArn"],
                            tags=tags,
                        )
                    )
                except Exception as e:
                    print(
                        f"Error getting tags for function {function['FunctionName']}: {e}"
                    )

        return functions

    def extract_service_info(self, function: LambdaFunction) -> Optional[ServiceInfo]:
        tags = function.tags
        if "AppVersion" not in tags:
            return None

        stack = tags.get("Stack", "Unknown")
        service = f"{stack}-{tags.get('Service', 'Unknown')}"
        env = tags.get("Environment", "Unknown")
        terraform = tags.get("TerraformVersion", "Unknown")

        return ServiceInfo(
            env=env, service=service, stack=stack, terraform_version=terraform
        )

    def publish_lambda_metrics(
        self, function: LambdaFunction, service_info: ServiceInfo
    ) -> None:
        dimensions = [
            {"Name": "Env", "Value": service_info.env},
            {"Name": "Service", "Value": service_info.service},
            {"Name": "Stack", "Value": service_info.stack},
            {"Name": "FunctionName", "Value": function.name},
            {"Name": "AppVersion", "Value": function.tags["AppVersion"]},
        ]

        self.cloudwatch_client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    "MetricName": "lambdaTag",
                    "Dimensions": dimensions,
                    "Value": 1,
                    "Unit": "Count",
                }
            ],
        )

    def publish_terraform_metrics(self, service_info: ServiceInfo) -> None:
        dimensions = [
            {"Name": "Env", "Value": service_info.env},
            {"Name": "Service", "Value": service_info.service},
            {"Name": "Stack", "Value": service_info.stack},
            {"Name": "TerraformVersion", "Value": service_info.terraform_version},
        ]

        self.cloudwatch_client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    "MetricName": "terraformTag",
                    "Dimensions": dimensions,
                    "Value": 1,
                    "Unit": "Count",
                }
            ],
        )


def lambda_handler(event, context):
    inspector = LambdaInspector()
    functions = inspector.get_all_functions()
    services: Set[ServiceInfo] = set()

    for function in functions:
        service_info = inspector.extract_service_info(function)
        if service_info:
            services.add(service_info)
            try:
                inspector.publish_lambda_metrics(function, service_info)
                print(
                    f"Published metric for {function.name} AppVersion {function.tags['AppVersion']}, Stack {service_info.stack}"
                )
            except Exception as e:
                print(f"Error processing function {function.name}: {e}")

    for service_info in services:
        try:
            inspector.publish_terraform_metrics(service_info)
            print(
                f"Published terraformTag metric for Service {service_info.service}, Stack {service_info.stack}, Env {service_info.env}, TerraformVersion {service_info.terraform_version}"
            )
        except Exception as e:
            print(f"Error publishing terraform metrics for {service_info.service}: {e}")

    return {"statusCode": 200, "body": "Metrics updated successfully"}
