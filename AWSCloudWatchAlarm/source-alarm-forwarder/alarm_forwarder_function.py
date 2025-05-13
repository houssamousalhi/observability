import json
import os
from collections import defaultdict
from datetime import UTC, datetime
import boto3

CLOUDWATCH_NAMESPACE = os.environ.get("CLOUDWATCH_NAMESPACE", "CloudWatchAlarms")


def get_resource_info(alarm):
    """Extract resource information from alarm dimensions and metrics."""
    resource_type = None
    resource_id = None
    resource_details = {}

    # First try to get resource info from alarm dimensions
    dimensions = alarm.get("Dimensions", [])
    for dimension in dimensions:
        if dimension["Value"]:  # Only add non-empty values
            resource_details[dimension["Name"]] = dimension["Value"]
            if dimension["Name"] in [
                "QueueName",
                "FunctionName",
                "InstanceId",
                "DBInstanceIdentifier",
                "LoadBalancerName",
                "AutoScalingGroupName",
                "TopicName",
                "TableName",
                "BucketName",
                "ApiId",
                "ApiName",
                "StateMachineArn",
                "ExecutionId",
                "ActivityArn",
            ]:
                resource_id = dimension["Value"]

    # Get namespace and use it as primary resource type
    namespace = alarm.get("Namespace", "")
    if namespace:
        # Remove 'AWS/' prefix if present
        resource_type = namespace.replace("AWS/", "")
        resource_details["namespace"] = namespace

    # If no dimensions in alarm, try to get from metrics
    if not dimensions and "Metrics" in alarm:
        for metric in alarm["Metrics"]:
            if "MetricStat" in metric and "Metric" in metric["MetricStat"]:
                metric_info = metric["MetricStat"]["Metric"]
                namespace = metric_info.get("Namespace", "")
                if namespace and not resource_type:
                    resource_type = namespace.replace("AWS/", "")
                    resource_details["namespace"] = namespace

                for dimension in metric_info.get("Dimensions", []):
                    if dimension["Value"]:
                        resource_details[dimension["Name"]] = dimension["Value"]
                        if dimension["Name"] in [
                            "QueueName",
                            "FunctionName",
                            "InstanceId",
                            "DBInstanceIdentifier",
                            "LoadBalancerName",
                            "AutoScalingGroupName",
                            "TopicName",
                            "TableName",
                            "BucketName",
                            "ApiId",
                            "ApiName",
                            "StateMachineArn",
                            "ExecutionId",
                            "ActivityArn",
                        ]:
                            resource_id = dimension["Value"]

    # If still no resource type, try to get from namespace in metrics
    if not resource_type and "Metrics" in alarm:
        for metric in alarm["Metrics"]:
            if "MetricStat" in metric and "Metric" in metric["MetricStat"]:
                namespace = metric["MetricStat"]["Metric"].get("Namespace", "")
                if namespace:
                    resource_type = namespace.replace("AWS/", "")
                    resource_details["namespace"] = namespace
                    break

    # Add alarm information
    if alarm.get("AlarmName"):
        resource_details["alarm_name"] = alarm["AlarmName"]
    if alarm.get("AlarmDescription"):
        try:
            # Try to parse JSON description
            desc_json = json.loads(alarm["AlarmDescription"])
            resource_details.update(desc_json)
        except json.JSONDecodeError:
            resource_details["alarm_description"] = alarm["AlarmDescription"]

    return resource_type, resource_id, resource_details


def count_alarms_by_resource_type(alarms):
    """Count alarms by resource type and state."""
    resource_type_counts = defaultdict(
        lambda: {"alarm_count": 0, "ok_count": 0, "insufficient_count": 0}
    )

    for alarm in alarms:
        resource_type, _, _ = get_resource_info(alarm)
        resource_type = resource_type if resource_type else "Unknown"

        if alarm["StateValue"] == "ALARM":
            resource_type_counts[resource_type]["alarm_count"] += 1
        elif alarm["StateValue"] == "OK":
            resource_type_counts[resource_type]["ok_count"] += 1
        elif alarm["StateValue"] == "INSUFFICIENT_DATA":
            resource_type_counts[resource_type]["insufficient_count"] += 1

    return resource_type_counts


def print_resource_metrics(resource_type_counts):
    """Print metrics for each resource type."""
    print("\n=== Resource Type Level Alarm Metrics ===")
    for resource_type, counts in sorted(resource_type_counts.items()):
        print(f"\nResource Type: {resource_type}")
        print(f"  Alarms in ALARM state: {counts['alarm_count']}")
        print(f"  Alarms in OK state: {counts['ok_count']}")
        print(f"  Alarms in INSUFFICIENT_DATA state: {counts['insufficient_count']}")


def put_resource_metrics(cloudwatch, resource_type_counts):
    """Put metrics to CloudWatch for each resource type."""
    for resource_type, counts in resource_type_counts.items():
        cloudwatch.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    "MetricName": "ResourceTypeAlarmsInAlarmState",
                    "Dimensions": [{"Name": "ResourceType", "Value": resource_type}],
                    "Value": counts["alarm_count"],
                    "Unit": "Count",
                    "Timestamp": datetime.now(UTC),
                },
                {
                    "MetricName": "ResourceTypeAlarmsInOkState",
                    "Dimensions": [{"Name": "ResourceType", "Value": resource_type}],
                    "Value": counts["ok_count"],
                    "Unit": "Count",
                    "Timestamp": datetime.now(UTC),
                },
                {
                    "MetricName": "ResourceTypeAlarmsInInsufficientState",
                    "Dimensions": [{"Name": "ResourceType", "Value": resource_type}],
                    "Value": counts["insufficient_count"],
                    "Unit": "Count",
                    "Timestamp": datetime.now(UTC),
                },
            ],
        )


def put_individual_alarm_metrics(cloudwatch, alarms_in_alarm):
    """Put metrics for individual alarms in ALARM state."""
    for alarm in alarms_in_alarm:
        resource_type, resource_id, resource_details = get_resource_info(alarm)

        dimensions = []
        if alarm.get("AlarmName"):
            dimensions.append({"Name": "AlarmName", "Value": alarm["AlarmName"]})

        if resource_type:
            dimensions.append({"Name": "ResourceType", "Value": resource_type})

        if resource_id:
            dimensions.append({"Name": "ResourceId", "Value": resource_id})

        for key, value in resource_details.items():
            if value and key not in ["alarm_name", "alarm_description"]:
                dimensions.append({"Name": key, "Value": str(value)})

        if dimensions:
            cloudwatch.put_metric_data(
                Namespace=CLOUDWATCH_NAMESPACE,
                MetricData=[
                    {
                        "MetricName": "ActiveAlarm",
                        "Dimensions": dimensions,
                        "Value": 1,
                        "Unit": "Count",
                        "Timestamp": datetime.now(UTC),
                    }
                ],
            )
            print(f"Dimensions: {dimensions}")
            print(f"State Value: {alarm.get('StateValue', '')}")
            print("---")


def lambda_handler(event, context):
    cloudwatch = boto3.client("cloudwatch")

    # List all alarms
    alarms = []
    paginator = cloudwatch.get_paginator("describe_alarms")
    for page in paginator.paginate():
        alarms.extend(page["MetricAlarms"])

    # Filter alarms to only those in ALARM state
    alarms_in_alarm = [alarm for alarm in alarms if alarm["StateValue"] == "ALARM"]

    # Count alarms by resource type
    resource_type_counts = count_alarms_by_resource_type(alarms)

    # Print metrics
    print_resource_metrics(resource_type_counts)

    # Put metrics to CloudWatch
    put_resource_metrics(cloudwatch, resource_type_counts)
    put_individual_alarm_metrics(cloudwatch, alarms_in_alarm)

    return {
        "statusCode": 200,
        "body": f"Successfully processed {len(alarms_in_alarm)} alarms in ALARM state",
    }


if __name__ == "__main__":
    lambda_handler({}, {})
