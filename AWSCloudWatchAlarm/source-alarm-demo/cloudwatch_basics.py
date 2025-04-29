"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon CloudWatch to create
and manage custom metrics and alarms.
"""

# snippet-start:[python.example_code.cloudwatch.imports]
from datetime import datetime, timedelta, UTC
import logging
from pprint import pprint
import random
import time
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# snippet-end:[python.example_code.cloudwatch.imports]


# snippet-start:[python.example_code.cloudwatch.CloudWatchWrapper]
class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""

    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource
        self.cloudwatch_client = boto3.client("cloudwatch")

    # snippet-end:[python.example_code.cloudwatch.CloudWatchWrapper]

    # snippet-start:[python.example_code.cloudwatch.ListMetrics]
    def list_metrics(self, namespace, name, recent=False):
        """
        Gets the metrics within a namespace that have the specified name.
        If the metric has no dimensions, a single metric is returned.
        Otherwise, metrics for all dimensions are returned.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param recent: When True, only metrics that have been active in the last
                       three hours are returned.
        :return: An iterator that yields the retrieved metrics.
        """
        try:
            kwargs = {"Namespace": namespace, "MetricName": name}
            if recent:
                kwargs["RecentlyActive"] = "PT3H"  # List past 3 hours only
            metric_iter = self.cloudwatch_resource.metrics.filter(**kwargs)
            logger.info("Got metrics for %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't get metrics for %s.%s.", namespace, name)
            raise
        else:
            return metric_iter

    # snippet-end:[python.example_code.cloudwatch.ListMetrics]

    # snippet-start:[python.example_code.cloudwatch.PutMetricData]
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

    # snippet-end:[python.example_code.cloudwatch.PutMetricData]

    # snippet-start:[python.example_code.cloudwatch.PutMetricData_DataSet]
    def put_metric_data_set(self, namespace, name, timestamp, unit, data_set):
        """
        Sends a set of data to CloudWatch for a metric. All of the data in the set
        have the same timestamp and unit.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param timestamp: The UTC timestamp for the metric.
        :param unit: The unit of the metric.
        :param data_set: The set of data to send. This set is a dictionary that
                         contains a list of values and a list of corresponding counts.
                         The value and count lists must be the same length.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            metric.put_data(
                Namespace=namespace,
                MetricData=[
                    {
                        "MetricName": name,
                        "Timestamp": timestamp,
                        "Values": data_set["values"],
                        "Counts": data_set["counts"],
                        "Unit": unit,
                    }
                ],
            )
            logger.info("Put data set for metric %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't put data set for metric %s.%s.", namespace, name)
            raise

    # snippet-end:[python.example_code.cloudwatch.PutMetricData_DataSet]

    # snippet-start:[python.example_code.cloudwatch.GetMetricStatistics]
    def get_metric_statistics(
        self, namespace, name, start, end, period, stat_types, dimensions=None
    ):
        """
        Gets statistics for a metric within a specified time span. Metrics are grouped
        into the specified period.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param start: The UTC start time of the time span to retrieve.
        :param end: The UTC end time of the time span to retrieve.
        :param period: The period, in seconds, in which to group metrics.
        :param stat_types: The type of statistics to retrieve.
        :param dimensions: The dimensions of the metric.
        :return: The retrieved statistics for the metric.
        """
        try:
            params = {
                "Namespace": namespace,
                "MetricName": name,
                "StartTime": start,
                "EndTime": end,
                "Period": period,
                "Statistics": stat_types,
            }
            if dimensions:
                params["Dimensions"] = dimensions

            stats = self.cloudwatch_resource.get_metric_statistics(**params)
            logger.info(
                "Got %s statistics for %s.", len(stats["Datapoints"]), stats["Label"]
            )
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", namespace, name)
            raise
        else:
            return stats

    # snippet-end:[python.example_code.cloudwatch.GetMetricStatistics]

    # snippet-start:[python.example_code.cloudwatch.PutMetricAlarm]
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

    # snippet-end:[python.example_code.cloudwatch.PutMetricAlarm]

    # snippet-start:[python.example_code.cloudwatch.DescribeAlarmsForMetric]
    def get_metric_alarms(self, metric_namespace, metric_name):
        """
        Gets the alarms that are currently watching the specified metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :returns: An iterator that yields the alarms.
        """
        metric = self.cloudwatch_resource.Metric(metric_namespace, metric_name)
        alarm_iter = metric.alarms.all()
        logger.info("Got alarms for metric %s.%s.", metric_namespace, metric_name)
        return alarm_iter

    # snippet-end:[python.example_code.cloudwatch.DescribeAlarmsForMetric]

    # snippet-start:[python.example_code.cloudwatch.EnableAlarmActions.DisableAlarmActions]
    def enable_alarm_actions(self, alarm_name, enable):
        """
        Enables or disables actions on the specified alarm. Alarm actions can be
        used to send notifications or automate responses when an alarm enters a
        particular state.

        :param alarm_name: The name of the alarm.
        :param enable: When True, actions are enabled for the alarm. Otherwise, they
                       disabled.
        """
        try:
            alarm = self.cloudwatch_resource.Alarm(alarm_name)
            if enable:
                alarm.enable_actions()
            else:
                alarm.disable_actions()
            logger.info(
                "%s actions for alarm %s.",
                "Enabled" if enable else "Disabled",
                alarm_name,
            )
        except ClientError:
            logger.exception(
                "Couldn't %s actions alarm %s.",
                "enable" if enable else "disable",
                alarm_name,
            )
            raise

    # snippet-end:[python.example_code.cloudwatch.EnableAlarmActions.DisableAlarmActions]

    # snippet-start:[python.example_code.cloudwatch.DeleteAlarms]
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

    # snippet-end:[python.example_code.cloudwatch.DeleteAlarms]

    def set_alarms_to_ok_state(self, services, alarms, period):
        """
        Sends datapoints to set all alarms to OK state.

        :param services: Dictionary of services and their configurations
        :param alarms: Dictionary of created alarms
        :param period: The period to wait between datapoints
        """
        print("\nSetting alarms to OK state...")
        for _ in range(1):  # Send 1 data point
            for namespace, configs in services.items():
                for config in configs:
                    # Send values below threshold to set OK state
                    if (
                        namespace == "SQS"
                        and config["metric_name"] == "NumberOfMessagesReceived"
                    ):
                        value = random.randint(500, 800)  # Below SQS threshold
                    elif (
                        namespace == "SQS"
                        and config["metric_name"]
                        == "ApproximateNumberOfMessagesVisible"
                    ):
                        value = 0  # No messages in DLQ
                    elif namespace == "Lambda" and config["metric_name"] == "Errors":
                        value = random.randint(0, 2)  # Below Lambda threshold
                    elif namespace == "Lambda" and config["metric_name"] == "Duration":
                        value = random.randint(1000, 5000)  # Below processing threshold
                    else:  # Lambda Invocations or API Gateway
                        value = random.randint(0, 5)  # Below threshold

                    self.put_metric_data(
                        namespace,
                        config["metric_name"],
                        value,
                        config["unit"],
                        config["dimensions"],
                    )
            time.sleep(period)  # Wait one period between data points

    def set_alarms_to_alarm_state(self, services, alarms, period):
        """
        Sends datapoints to set all alarms to ALARM state.

        :param services: Dictionary of services and their configurations
        :param alarms: Dictionary of created alarms
        :param period: The period to wait between datapoints
        """
        print("\nSetting alarms to ALARM state...")
        for _ in range(2):  # Send 2 data points
            for namespace, configs in services.items():
                for config in configs:
                    # Send values above threshold to trigger alarms
                    if (
                        namespace == "SQS"
                        and config["metric_name"] == "NumberOfMessagesReceived"
                    ):
                        value = random.randint(1100, 1500)  # Above SQS threshold
                    elif (
                        namespace == "SQS"
                        and config["metric_name"]
                        == "ApproximateNumberOfMessagesVisible"
                    ):
                        value = random.randint(2, 5)  # Messages in DLQ
                    elif namespace == "Lambda" and config["metric_name"] == "Errors":
                        value = random.randint(6, 10)  # Above Lambda threshold
                    elif namespace == "Lambda" and config["metric_name"] == "Duration":
                        value = random.randint(
                            12000, 15000
                        )  # Above processing threshold
                    else:  # Lambda Invocations or API Gateway
                        value = random.randint(120, 150)  # Above threshold

                    self.put_metric_data(
                        namespace,
                        config["metric_name"],
                        value,
                        config["unit"],
                        config["dimensions"],
                    )
            time.sleep(period)  # Wait one period between data points


# snippet-start:[python.example_code.cloudwatch.Usage_MetricsAlarms]
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
    }

    minutes = 20
    start = datetime.now(UTC) - timedelta(minutes=minutes)
    period = 60  # 1 minute period
    eval_periods = 1  # Changed to 1 evaluation period

    # Create alarms for each service
    alarms = {}
    for namespace, configs in services.items():
        for config in configs:
            print(f"\nCreating alarm for {namespace}...")
            alarm_name = f"{namespace}-{config['metric_name']}-alarm"
            alarm = cw_wrapper.create_metric_alarm(
                namespace,
                config["metric_name"],
                alarm_name,
                "Maximum",
                period,
                eval_periods,
                config["threshold"],
                "GreaterThanThreshold",
                config["dimensions"],
            )
            alarms[alarm_name] = alarm
            print(f"Alarm {alarm_name} created with ARN: {alarm['AlarmArn']}")

    # Set initial OK state
    cw_wrapper.set_alarms_to_ok_state(services, alarms, period)

    # Set alarms to ALARM state
    cw_wrapper.set_alarms_to_alarm_state(services, alarms, period)

    # Check alarm states
    print("\nChecking alarm states...")
    for alarm_name in alarms:
        response = cw_wrapper.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
        alarm = response["MetricAlarms"][0]
        print(f"Alarm {alarm_name} is in state: {alarm['StateValue']}")

    # Return alarms to OK state
    cw_wrapper.set_alarms_to_ok_state(services, alarms, period)

    # Check final alarm states
    print("\nChecking final alarm states...")
    for alarm_name in alarms:
        response = cw_wrapper.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
        alarm = response["MetricAlarms"][0]
        print(f"Alarm {alarm_name} is in state: {alarm['StateValue']}")

    time.sleep(2 * period)
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


# snippet-end:[python.example_code.cloudwatch.Usage_MetricsAlarms]


if __name__ == "__main__":
    usage_demo()
