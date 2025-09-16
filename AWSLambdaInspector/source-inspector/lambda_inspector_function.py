import os
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta

import boto3

CLOUDWATCH_NAMESPACE = os.environ.get("CLOUDWATCH_NAMESPACE", "StackRef")


# Configuration Constants
class TagNames:
    """AWS resource tag names"""

    APP_VERSION = "AppVersion"
    TERRAFORM_VERSION = "TerraformVersion"
    ENVIRONMENT = "Environment"
    SERVICE = "Service"
    STACK = "Stack"


class DimensionNames:
    """CloudWatch metric dimension names"""

    ENV = "Env"
    SERVICE = "Service"
    STACK = "Stack"
    FUNCTION_NAME = "FunctionName"
    APP_VERSION = "AppVersion"
    TERRAFORM_VERSION = "TerraformVersion"


class MetricNames:
    """CloudWatch metric names"""

    LAMBDA_TAG = "lambdaTag"
    TERRAFORM_TAG = "terraformTag"


class Config:
    """Configuration values"""

    METRIC_UNIT = "Count"
    UNKNOWN_VALUE = "Unknown"
    HISTORY_DAYS_LOOKBACK = 365
    RECENT_DAYS_CUTOFF = 0
    CONFIG_HISTORY_LIMIT = 100
    AWS_LAMBDA_FUNCTION_RESOURCE_TYPE = "AWS::Lambda::Function"


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


@dataclass
class MetricsData:
    metric_name: str
    dimensions: List[Dict[str, str]]
    value: float
    unit: str

    def to_cloudwatch_format(self) -> Dict:
        """Convert to CloudWatch metric data format."""
        return {
            "MetricName": self.metric_name,
            "Dimensions": self.dimensions,
            "Value": self.value,
            "Unit": self.unit,
        }


class LambdaInspector:
    def __init__(self):
        self.lambda_client = boto3.client("lambda")
        self.cloudwatch_client = boto3.client("cloudwatch")
        self.config_client = boto3.client("config")

    def get_all_functions(self) -> List[LambdaFunction]:
        functions = []
        all_functions_count = 0
        functions_with_app_version = 0
        paginator = self.lambda_client.get_paginator("list_functions")

        for page in paginator.paginate():
            for function in page["Functions"]:
                all_functions_count += 1
                try:
                    tags = self.lambda_client.list_tags(
                        Resource=function["FunctionArn"]
                    ).get("Tags", {})

                    # Only include functions that have the AppVersion tag
                    if TagNames.APP_VERSION in tags:
                        functions_with_app_version += 1
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

        print(f"Total functions found: {all_functions_count}")
        print(f"Functions with AppVersion tag: {functions_with_app_version}")

        # Sort functions by environment, stack, and service
        def sort_key(func: LambdaFunction) -> Tuple[str, str, str]:
            service_info = self.extract_service_info(func)
            return (service_info.env, service_info.stack, service_info.service)

        functions.sort(key=sort_key)
        return functions

    def extract_service_info(self, function: LambdaFunction) -> ServiceInfo:
        tags = function.tags
        stack = tags.get(TagNames.STACK, Config.UNKNOWN_VALUE)
        service = tags.get(TagNames.SERVICE, stack)
        env = tags.get(TagNames.ENVIRONMENT, Config.UNKNOWN_VALUE)
        terraform = tags.get(TagNames.TERRAFORM_VERSION, Config.UNKNOWN_VALUE)

        return ServiceInfo(
            env=env, service=service, stack=stack, terraform_version=terraform
        )

    def get_resource_history_tags(
        self,
        resource_id: str,
        resource_type: str,
        earlier_days: float,
        later_days: float,
    ) -> List[Dict]:
        """Get the configuration history for a specific resource from AWS Config."""
        try:
            paginator = self.config_client.get_paginator("get_resource_config_history")
            history_tags = []
            earlier_days_ago = datetime.now() - timedelta(days=earlier_days)
            later_days_ago = datetime.now() - timedelta(days=later_days)

            # Convert to UTC and format as required by AWS Config
            earlier_time_utc = earlier_days_ago.astimezone().isoformat()
            later_time_utc = later_days_ago.astimezone().isoformat()

            for page in paginator.paginate(
                resourceType=resource_type,
                resourceId=resource_id,
                earlierTime=earlier_time_utc,
                laterTime=later_time_utc,
                limit=Config.CONFIG_HISTORY_LIMIT,
            ):
                configuration_items = page.get("configurationItems", [])
                for item in configuration_items:
                    if item.get("tags") and item["tags"] != {}:
                        history_tags.append(item["tags"])

            return history_tags
        except Exception as e:
            print(f"Error getting resource history for {resource_id}: {e}")
            return []

    def get_tags_history(
        self, function: LambdaFunction, earlier_days: float, later_days: float
    ) -> Tuple[Set[str], Set[str]]:
        """Extract all AppVersion values from the resource history."""
        app_versions = set()
        terraform_versions = set()
        history_tags = self.get_resource_history_tags(
            function.name,
            Config.AWS_LAMBDA_FUNCTION_RESOURCE_TYPE,
            earlier_days,
            later_days,
        )

        # Only process configuration items that have tags AppVersion and TerraformVersion
        for tags in history_tags:
            if TagNames.APP_VERSION in tags:
                app_versions.add(tags[TagNames.APP_VERSION])
            if TagNames.TERRAFORM_VERSION in tags:
                terraform_versions.add(tags[TagNames.TERRAFORM_VERSION])

        return app_versions, terraform_versions

    def publish_metrics(
        self, metric_name: str, dimensions: List[Dict[str, str]], value: float
    ) -> None:
        metric_data = MetricsData(
            metric_name=metric_name,
            dimensions=dimensions,
            value=value,
            unit=Config.METRIC_UNIT,
        )

        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=CLOUDWATCH_NAMESPACE,
                MetricData=[metric_data.to_cloudwatch_format()],
            )
            print(f"Published metric for {metric_name} {dimensions} {value}")
        except Exception as e:
            print(
                f"Error publishing metric for {metric_name} {dimensions} {value}: {e}"
            )


def create_lambda_dimensions(
    service_info: ServiceInfo, function_name: str, app_version: str
) -> List[Dict[str, str]]:
    """Create dimensions for lambda metrics."""
    return [
        {"Name": DimensionNames.ENV, "Value": service_info.env},
        {"Name": DimensionNames.STACK, "Value": service_info.stack},
        {"Name": DimensionNames.SERVICE, "Value": service_info.service},
        {"Name": DimensionNames.FUNCTION_NAME, "Value": function_name},
        {"Name": DimensionNames.APP_VERSION, "Value": app_version},
    ]


def create_terraform_dimensions(
    service_info: ServiceInfo, terraform_version: str
) -> List[Dict[str, str]]:
    """Create dimensions for terraform metrics."""
    return [
        {"Name": DimensionNames.ENV, "Value": service_info.env},
        {"Name": DimensionNames.STACK, "Value": service_info.stack},
        {"Name": DimensionNames.SERVICE, "Value": service_info.service},
        {"Name": DimensionNames.TERRAFORM_VERSION, "Value": terraform_version},
    ]


def publish_lambda_metric(
    inspector: LambdaInspector,
    service_info: ServiceInfo,
    function_name: str,
    app_version: str,
    value: float = 1,
) -> None:
    """Publish a lambda metric with proper dimensions."""
    dimensions = create_lambda_dimensions(service_info, function_name, app_version)
    inspector.publish_metrics(MetricNames.LAMBDA_TAG, dimensions, value)


def publish_terraform_metric(
    inspector: LambdaInspector,
    service_info: ServiceInfo,
    terraform_version: str,
    value: float = 1,
) -> None:
    """Publish a terraform metric with proper dimensions."""
    dimensions = create_terraform_dimensions(service_info, terraform_version)
    inspector.publish_metrics(MetricNames.TERRAFORM_TAG, dimensions, value)


def lambda_handler(event, context):
    publish_metrics(include_history=True, earlier_days=1, later_days=0)
    return {"statusCode": 200, "body": "Metrics updated successfully"}


def publish_metrics(
    include_history: bool = False,
    earlier_days: float = Config.HISTORY_DAYS_LOOKBACK,
    later_days: float = Config.RECENT_DAYS_CUTOFF,
):
    inspector = LambdaInspector()
    functions = inspector.get_all_functions()
    service_terraform_versions: Dict[ServiceInfo, Set[str]] = {}

    lambda_metrics_count = 0
    terraform_metrics_count = 0

    for function in functions:
        service_info = inspector.extract_service_info(function)

        app_versions = {function.tags[TagNames.APP_VERSION]}
        terraform_versions = {function.tags[TagNames.TERRAFORM_VERSION]}

        if include_history:
            app_versions_history, terraform_versions_history = (
                inspector.get_tags_history(function, earlier_days, later_days)
            )
            app_versions.update(app_versions_history)
            terraform_versions.update(terraform_versions_history)

        if service_info not in service_terraform_versions:
            service_terraform_versions[service_info] = set()
        service_terraform_versions[service_info].update(terraform_versions)

        for version in app_versions:
            if version != function.tags.get(TagNames.APP_VERSION):
                publish_lambda_metric(
                    inspector, service_info, function.name, version, 0
                )
                lambda_metrics_count += 1
            else:
                publish_lambda_metric(
                    inspector,
                    service_info,
                    function.name,
                    function.tags[TagNames.APP_VERSION],
                    1,
                )
                lambda_metrics_count += 1

    for service_info, terraform_versions in service_terraform_versions.items():
        for version in terraform_versions:
            if version != service_info.terraform_version:
                publish_terraform_metric(inspector, service_info, version, 0)
                terraform_metrics_count += 1
            else:
                publish_terraform_metric(
                    inspector, service_info, service_info.terraform_version, 1
                )
                terraform_metrics_count += 1

    print(
        f"Total metrics published: {lambda_metrics_count} lambda metrics, {terraform_metrics_count} terraform metrics"
    )
    print("Published CW Metrics successfully")


if __name__ == "__main__":
    import sys

    # Start timing
    start_time = time.time()

    # Parse command line arguments with flexible parsing
    include_history = True
    earlier_days = Config.HISTORY_DAYS_LOOKBACK
    later_days = Config.RECENT_DAYS_CUTOFF

    if len(sys.argv) >= 2:
        include_history = sys.argv[1].lower() == "true"

    if len(sys.argv) >= 3:
        earlier_days = float(sys.argv[2])

    if len(sys.argv) >= 4:
        later_days = float(sys.argv[3])

    # Validate time range parameters to prevent AWS Config errors
    if earlier_days < 0 or later_days < 0:
        print("Error: Time range parameters must be non-negative")
        sys.exit(1)

    if earlier_days > 2555:  # AWS Config limit is 7 years (2555 days)
        print(
            "Warning: earlier_days exceeds AWS Config limit (2555 days), setting to 2555"
        )
        earlier_days = 2555

    if later_days > 2555:
        print(
            "Warning: later_days exceeds AWS Config limit (2555 days), setting to 2555"
        )
        later_days = 2555

    # AWS Config requires a minimum time difference between earlier and later times
    if earlier_days <= later_days:
        print(
            "Error: earlier_days must be greater than later_days for AWS Config to work properly"
        )
        print(f"Current values: earlier_days={earlier_days}, later_days={later_days}")
        print("Try using earlier_days=2, later_days=0 for a 2-day lookback")
        sys.exit(1)

    print(
        f"Running with args: include_history={include_history}, earlier_days={earlier_days}, later_days={later_days}"
    )

    publish_metrics(
        include_history=include_history,
        earlier_days=earlier_days,
        later_days=later_days,
    )

    # Calculate and print execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution completed in {execution_time:.2f} seconds")
