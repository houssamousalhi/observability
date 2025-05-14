"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon CloudWatch to create
and manage custom metrics and alarms.
"""

from datetime import datetime, timedelta, UTC
import logging
from pprint import pprint
import random
import time
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""

    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource
        self.cloudwatch_client = boto3.client("cloudwatch")

    def put_metric_data(self, namespace, name, value, unit, dimensions=None):
        """
        Sends a single data value to CloudWatch for a metric. This metric is given
        a timestamp of the current UTC time.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param value: The value of the metric.
        :param unit: The unit of the metric.
        :param dimensions: The dimensions of the metric.
        """
        try:
            metric_data = {
                "MetricName": name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.now(UTC),
            }
            if dimensions:
                metric_data["Dimensions"] = dimensions

            self.cloudwatch_client.put_metric_data(
                Namespace=namespace, MetricData=[metric_data]
            )
            logger.info("Put data for metric %s.%s", namespace, name)
        except ClientError:
            logger.exception("Couldn't put data for metric %s.%s", namespace, name)
            raise

    def create_metric_alarm(
        self,
        metric_namespace,
        metric_name,
        alarm_name,
        stat_type,
        period,
        eval_periods,
        threshold,
        comparison_op,
        dimensions=None,
    ):
        """
        Creates an alarm that watches a metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :param alarm_name: The name of the alarm.
        :param stat_type: The type of statistic the alarm watches.
        :param period: The period in which metric data are grouped to calculate
                       statistics.
        :param eval_periods: The number of periods that the metric must be over the
                             alarm threshold before the alarm is set into an alarmed
                             state.
        :param threshold: The threshold value to compare against the metric statistic.
        :param comparison_op: The comparison operation used to compare the threshold
                              against the metric.
        :param dimensions: The dimensions of the metric.
        :return: The alarm details.
        """
        try:
            alarm_params = {
                "AlarmName": alarm_name,
                "MetricName": metric_name,
                "Namespace": metric_namespace,
                "Statistic": stat_type,
                "Period": period,
                "EvaluationPeriods": eval_periods,
                "Threshold": threshold,
                "ComparisonOperator": comparison_op,
                "TreatMissingData": "notBreaching",
            }
            if dimensions:
                alarm_params["Dimensions"] = dimensions

            self.cloudwatch_client.put_metric_alarm(**alarm_params)
            logger.info(
                "Added alarm %s to track metric %s.%s.",
                alarm_name,
                metric_namespace,
                metric_name,
            )

            # Get the alarm details
            response = self.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
            return response["MetricAlarms"][0]
        except ClientError:
            logger.exception(
                "Couldn't add alarm %s to metric %s.%s",
                alarm_name,
                metric_namespace,
                metric_name,
            )
            raise

    def delete_metric_alarms(self, namespace, metric_name, dimensions=None):
        """
        Deletes all of the alarms that are currently watching the specified metric.

        :param namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :param dimensions: The dimensions of the metric.
        """
        try:
            # First, describe the alarms to get their names
            params = {"MetricName": metric_name, "Namespace": namespace}
            if dimensions:
                params["Dimensions"] = dimensions

            response = self.cloudwatch_client.describe_alarms_for_metric(**params)
            alarm_names = [alarm["AlarmName"] for alarm in response["MetricAlarms"]]

            if alarm_names:
                self.cloudwatch_client.delete_alarms(AlarmNames=alarm_names)
                logger.info("Deleted alarms for metric %s.%s.", namespace, metric_name)
        except ClientError:
            logger.exception(
                "Couldn't delete alarms for metric %s.%s.",
                namespace,
                metric_name,
            )
            raise

    def set_alarms_to_ok_state(self, services, period, count=1):
        """
        Sends datapoints to set all alarms to OK state.

        :param services: Dictionary of services and their configurations
        :param period: The period to wait between datapoints
        """
        print("\nSetting alarms to OK state...")
        for _ in range(count):
            for namespace, configs in services.items():
                for config in configs:
                    # Send values below threshold to set OK state
                    if namespace == "SQS":
                        if config["metric_name"] == "NumberOfMessagesReceived":
                            value = random.randint(500, 800)  # Below SQS threshold
                        else:  # ApproximateNumberOfMessagesVisible
                            value = 0  # No messages in DLQ
                    elif namespace == "Lambda":
                        if config["metric_name"] == "Errors":
                            value = random.randint(0, 2)  # Below Lambda threshold
                        elif config["metric_name"] == "Duration":
                            value = random.randint(
                                1000, 5000
                            )  # Below processing threshold
                        else:  # Invocations
                            value = random.randint(0, 5)  # Below threshold
                    elif namespace == "ApiGateway":
                        value = random.randint(0, 5)  # Below threshold
                    elif namespace == "RDS":
                        if config["metric_name"] == "CPUUtilization":
                            value = random.randint(20, 60)  # Below CPU threshold
                        elif config["metric_name"] == "FreeStorageSpace":
                            value = random.randint(
                                5000000000, 8000000000
                            )  # 5-8GB free (well above 1GB threshold)
                        else:  # DatabaseConnections
                            value = random.randint(10, 50)  # Below connection threshold
                    elif namespace == "ECS":
                        if config["metric_name"] == "CPUUtilization":
                            value = random.randint(20, 60)  # Below CPU threshold
                        else:  # MemoryUtilization
                            value = random.randint(30, 70)  # Below memory threshold
                    elif namespace == "EC2":
                        if config["metric_name"] == "CPUUtilization":
                            value = random.randint(20, 60)  # Below CPU threshold
                        else:  # DiskSpaceUtilization
                            value = random.randint(30, 70)  # Below disk threshold
                    elif namespace == "DynamoDB":
                        value = random.randint(100, 500)  # Below capacity threshold
                    elif namespace == "ElastiCache":
                        if config["metric_name"] == "CPUUtilization":
                            value = random.randint(20, 60)  # Below CPU threshold
                        else:  # DatabaseMemoryUsagePercentage
                            value = random.randint(30, 70)  # Below memory threshold

                    self.put_metric_data(
                        namespace,
                        config["metric_name"],
                        value,
                        config["unit"],
                        config["dimensions"],
                    )
            time.sleep(period)  # Wait one period between data points

    def trigger_random_alerts(self, services, period, nb_alerts=1):
        """
        Randomly triggers alerts for different services.

        :param services: Dictionary of services and their configurations
        :param period: The period to wait between alerts
        :param nb_alerts: Number of random alerts to trigger
        """
        print("\nTriggering random alerts...")
        print("=" * 50)
        print("Alert Schedule:")
        print("=" * 50)

        for i in range(nb_alerts):
            # Randomly select a service
            namespace = random.choice(list(services.keys()))
            config = random.choice(services[namespace])

            print(f"\nAlert #{i+1}:")
            print(f"Service: {namespace}")
            print(f"Metric: {config['metric_name']}")
            print(f"Threshold: {config['threshold']} {config['unit']}")
            print(f"Dimensions: {config['dimensions']}")

            # Generate a value above threshold to trigger alarm
            if namespace == "SQS":
                if config["metric_name"] == "NumberOfMessagesReceived":
                    value = random.randint(1100, 1500)
                else:  # ApproximateNumberOfMessagesVisible
                    value = random.randint(2, 5)
            elif namespace == "Lambda":
                if config["metric_name"] == "Errors":
                    value = random.randint(6, 10)
                elif config["metric_name"] == "Duration":
                    value = random.randint(12000, 15000)
                else:  # Invocations
                    value = random.randint(120, 150)
            elif namespace == "ApiGateway":
                value = random.randint(15, 20)
            elif namespace == "RDS":
                if config["metric_name"] == "CPUUtilization":
                    value = random.randint(85, 95)
                elif config["metric_name"] == "FreeStorageSpace":
                    value = random.randint(
                        200000000, 500000000
                    )  # 200MB-500MB free (below 1GB threshold)
                else:  # DatabaseConnections
                    value = random.randint(120, 150)
            elif namespace == "ECS":
                if config["metric_name"] == "CPUUtilization":
                    value = random.randint(85, 95)
                else:  # MemoryUtilization
                    value = random.randint(90, 95)
            elif namespace == "EC2":
                if config["metric_name"] == "CPUUtilization":
                    value = random.randint(85, 95)
                else:  # DiskSpaceUtilization
                    value = random.randint(90, 95)
            elif namespace == "DynamoDB":
                value = random.randint(1200, 1500)
            elif namespace == "ElastiCache":
                if config["metric_name"] == "CPUUtilization":
                    value = random.randint(85, 95)
                else:  # DatabaseMemoryUsagePercentage
                    value = random.randint(90, 95)

            print(f"Triggering value: {value} {config['unit']}")

            self.put_metric_data(
                namespace,
                config["metric_name"],
                value,
                config["unit"],
                config["dimensions"],
            )

            # Wait for a random number of periods (1-3)
            wait_time = random.randint(1, 3) * period
            print(
                f"\nWaiting {wait_time} seconds ({wait_time/period} periods) before next alert..."
            )
            time.sleep(wait_time)

            # Check and print the alarm state
            alarm_name = f"{namespace}-{config['metric_name']}-alarm"
            response = self.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
            alarm = response["MetricAlarms"][0]
            print(f"Current alarm state: {alarm['StateValue']}")
            print("-" * 50)


def usage_demo():
    print("-" * 88)
    print("Welcome to the Amazon CloudWatch AWS Service Alarms demo!")
    print("-" * 88)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    cw_wrapper = CloudWatchWrapper(boto3.resource("cloudwatch"))

    # Simulate different AWS service metrics
    services = {
        "SQS": [
            {
                "metric_name": "NumberOfMessagesReceived",
                "dimensions": [{"Name": "QueueName", "Value": "demo-queue-1"}],
                "unit": "Count",
                "threshold": 1000,
            },
            {
                "metric_name": "ApproximateNumberOfMessagesVisible",
                "dimensions": [{"Name": "QueueName", "Value": "demo-queue-2"}],
                "unit": "Count",
                "threshold": 1,
            },
        ],
        "Lambda": [
            {
                "metric_name": "Errors",
                "dimensions": [{"Name": "FunctionName", "Value": "demo-function-1"}],
                "unit": "Count",
                "threshold": 5,
            },
            {
                "metric_name": "Duration",
                "dimensions": [{"Name": "FunctionName", "Value": "demo-function-2"}],
                "unit": "Milliseconds",
                "threshold": 10000,
            },
            {
                "metric_name": "Invocations",
                "dimensions": [{"Name": "FunctionName", "Value": "demo-function-3"}],
                "unit": "Count",
                "threshold": 100,
            },
        ],
        "ApiGateway": [
            {
                "metric_name": "5XXError",
                "dimensions": [{"Name": "ApiName", "Value": "demo-api"}],
                "unit": "Count",
                "threshold": 10,
            }
        ],
        "RDS": [
            {
                "metric_name": "CPUUtilization",
                "dimensions": [{"Name": "DBInstanceIdentifier", "Value": "demo-db-1"}],
                "unit": "Percent",
                "threshold": 80,
            },
            {
                "metric_name": "FreeStorageSpace",
                "dimensions": [{"Name": "DBInstanceIdentifier", "Value": "demo-db-1"}],
                "unit": "Bytes",
                "threshold": 1000000000,  # 1GB
            },
            {
                "metric_name": "DatabaseConnections",
                "dimensions": [{"Name": "DBInstanceIdentifier", "Value": "demo-db-1"}],
                "unit": "Count",
                "threshold": 100,
            },
        ],
        "ECS": [
            {
                "metric_name": "CPUUtilization",
                "dimensions": [
                    {"Name": "ClusterName", "Value": "demo-cluster"},
                    {"Name": "ServiceName", "Value": "demo-service"},
                ],
                "unit": "Percent",
                "threshold": 80,
            },
            {
                "metric_name": "MemoryUtilization",
                "dimensions": [
                    {"Name": "ClusterName", "Value": "demo-cluster"},
                    {"Name": "ServiceName", "Value": "demo-service"},
                ],
                "unit": "Percent",
                "threshold": 85,
            },
        ],
        "EC2": [
            {
                "metric_name": "CPUUtilization",
                "dimensions": [{"Name": "InstanceId", "Value": "i-1234567890abcdef0"}],
                "unit": "Percent",
                "threshold": 80,
            },
            {
                "metric_name": "DiskSpaceUtilization",
                "dimensions": [{"Name": "InstanceId", "Value": "i-1234567890abcdef0"}],
                "unit": "Percent",
                "threshold": 85,
            },
        ],
        "DynamoDB": [
            {
                "metric_name": "ConsumedWriteCapacityUnits",
                "dimensions": [{"Name": "TableName", "Value": "demo-table"}],
                "unit": "Count",
                "threshold": 1000,
            },
            {
                "metric_name": "ConsumedReadCapacityUnits",
                "dimensions": [{"Name": "TableName", "Value": "demo-table"}],
                "unit": "Count",
                "threshold": 1000,
            },
        ],
        "ElastiCache": [
            {
                "metric_name": "CPUUtilization",
                "dimensions": [{"Name": "CacheClusterId", "Value": "demo-cache"}],
                "unit": "Percent",
                "threshold": 80,
            },
            {
                "metric_name": "DatabaseMemoryUsagePercentage",
                "dimensions": [{"Name": "CacheClusterId", "Value": "demo-cache"}],
                "unit": "Percent",
                "threshold": 85,
            },
        ],
    }

    period = 60  # 1 minute period
    eval_periods = 1  # Changed to 1 evaluation period

    # Create alarms for each service
    alarms = {}
    for namespace, configs in services.items():
        for config in configs:
            print(f"\nCreating alarm for {namespace}...")
            alarm_name = f"{namespace}-{config['metric_name']}-alarm"

            # Use LessThanThreshold for FreeStorageSpace, GreaterThanThreshold for others
            comparison_op = (
                "LessThanThreshold"
                if config["metric_name"] == "FreeStorageSpace"
                else "GreaterThanThreshold"
            )

            alarm = cw_wrapper.create_metric_alarm(
                namespace,
                config["metric_name"],
                alarm_name,
                "Maximum",
                period,
                eval_periods,
                config["threshold"],
                comparison_op,
                config["dimensions"],
            )
            alarms[alarm_name] = alarm
            print(f"Alarm {alarm_name} created with ARN: {alarm['AlarmArn']}")

    # Set initial OK state
    cw_wrapper.set_alarms_to_ok_state(services, period, count=1)

    # Trigger random alerts
    cw_wrapper.trigger_random_alerts(services, period, nb_alerts=2)

    # Return alarms to OK state
    cw_wrapper.set_alarms_to_ok_state(services, period, count=2)

    # Check final alarm states
    print("\nChecking final alarm states...")
    for alarm_name in alarms:
        response = cw_wrapper.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
        alarm = response["MetricAlarms"][0]
        print(f"Alarm {alarm_name} is in state: {alarm['StateValue']}")

    # Delete alarms
    print("\nDeleting alarms...")
    for namespace, configs in services.items():
        for config in configs:
            alarm_name = f"{namespace}-{config['metric_name']}-alarm"
            cw_wrapper.delete_metric_alarms(
                namespace, config["metric_name"], config["dimensions"]
            )
            print(f"Deleted alarm {alarm_name}")

    print("\nThanks for watching!")
    print("-" * 88)


if __name__ == "__main__":
    usage_demo()
