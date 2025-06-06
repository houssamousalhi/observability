import os
import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from alarm_forwarder_function import (
    count_alarms_by_resource_type,
    get_resource_info,
    lambda_handler,
    print_resource_metrics,
    put_individual_alarm_metrics,
    put_resource_metrics,
)


@pytest.fixture
def mock_cloudwatch():
    mock = MagicMock()
    mock.get_paginator.return_value = MagicMock()
    return mock


def test_get_resource_info_from_dimensions():
    alarm = {
        "Dimensions": [
            {"Name": "QueueName", "Value": "test-queue"},
            {"Name": "FunctionName", "Value": "test-function"},
        ],
        "Namespace": "AWS/SQS",
        "AlarmName": "test-alarm",
        "AlarmDescription": '{"key": "value"}',
    }

    resource_type, resource_id, details = get_resource_info(alarm)

    assert resource_type == "SQS"
    assert resource_id == "test-function"
    assert details["QueueName"] == "test-queue"
    assert details["FunctionName"] == "test-function"
    assert details["namespace"] == "AWS/SQS"
    assert details["key"] == "value"


def test_get_resource_info_from_metrics():
    alarm = {
        "Metrics": [
            {
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/Lambda",
                        "Dimensions": [
                            {"Name": "FunctionName", "Value": "test-function"}
                        ],
                    }
                }
            }
        ],
        "AlarmName": "test-alarm",
    }

    resource_type, resource_id, details = get_resource_info(alarm)

    assert resource_type == "Lambda"
    assert resource_id == "test-function"
    assert details["FunctionName"] == "test-function"
    assert details["namespace"] == "AWS/Lambda"


def test_count_alarms_by_resource_type():
    alarms = [
        {"StateValue": "ALARM", "Namespace": "AWS/SQS"},
        {"StateValue": "OK", "Namespace": "AWS/SQS"},
        {"StateValue": "INSUFFICIENT_DATA", "Namespace": "AWS/Lambda"},
    ]

    counts = count_alarms_by_resource_type(alarms)

    assert counts["SQS"]["alarm_count"] == 1
    assert counts["SQS"]["ok_count"] == 1
    assert counts["SQS"]["insufficient_count"] == 0
    assert counts["Lambda"]["alarm_count"] == 0
    assert counts["Lambda"]["ok_count"] == 0
    assert counts["Lambda"]["insufficient_count"] == 1


def test_print_resource_metrics(capsys):
    resource_type_counts = {
        "SQS": {"alarm_count": 2, "ok_count": 1, "insufficient_count": 0},
        "Lambda": {"alarm_count": 0, "ok_count": 3, "insufficient_count": 1},
    }

    print_resource_metrics(resource_type_counts)
    captured = capsys.readouterr()

    assert "=== Resource Type Level Alarm Metrics ===" in captured.out
    assert "Resource Type: Lambda" in captured.out
    assert "Alarms in ALARM state: 0" in captured.out
    assert "Alarms in OK state: 3" in captured.out
    assert "Alarms in INSUFFICIENT_DATA state: 1" in captured.out


def test_put_resource_metrics(mock_cloudwatch):
    resource_type_counts = {
        "SQS": {"alarm_count": 2, "ok_count": 1, "insufficient_count": 0}
    }

    put_resource_metrics(mock_cloudwatch, resource_type_counts)

    mock_cloudwatch.put_metric_data.assert_called_once()
    metric_data = mock_cloudwatch.put_metric_data.call_args[1]["MetricData"]
    assert len(metric_data) == 3

    alarm_metric = next(
        m for m in metric_data if m["MetricName"] == "ResourceTypeAlarmsInAlarmState"
    )
    ok_metric = next(
        m for m in metric_data if m["MetricName"] == "ResourceTypeAlarmsInOkState"
    )
    insufficient_metric = next(
        m
        for m in metric_data
        if m["MetricName"] == "ResourceTypeAlarmsInInsufficientState"
    )

    assert alarm_metric["Value"] == 2
    assert ok_metric["Value"] == 1
    assert insufficient_metric["Value"] == 0


def test_put_individual_alarm_metrics(mock_cloudwatch, capsys):
    alarms_in_alarm = [
        {
            "StateValue": "ALARM",
            "AlarmName": "test-alarm",
            "Namespace": "AWS/SQS",
            "Dimensions": [{"Name": "QueueName", "Value": "test-queue"}],
        }
    ]

    put_individual_alarm_metrics(mock_cloudwatch, alarms_in_alarm)

    mock_cloudwatch.put_metric_data.assert_called_once()
    metric_data = mock_cloudwatch.put_metric_data.call_args[1]["MetricData"]
    assert len(metric_data) == 1
    assert metric_data[0]["MetricName"] == "ActiveAlarm"
    assert metric_data[0]["Value"] == 1

    captured = capsys.readouterr()
    assert "Dimensions:" in captured.out
    assert "State Value: ALARM" in captured.out


@patch("alarm_forwarder_function.boto3.client")
def test_lambda_handler(mock_boto3, mock_cloudwatch, capsys):
    mock_boto3.return_value = mock_cloudwatch
    mock_cloudwatch.get_paginator.return_value.paginate.return_value = [
        {
            "MetricAlarms": [
                {"StateValue": "ALARM", "Namespace": "AWS/SQS"},
                {"StateValue": "OK", "Namespace": "AWS/SQS"},
                {"StateValue": "INSUFFICIENT_DATA", "Namespace": "AWS/Lambda"},
            ]
        }
    ]

    response = lambda_handler({}, {})

    assert response["statusCode"] == 200
    assert response["body"] == "Successfully processed 1 alarms in ALARM state"

    mock_boto3.assert_called_once_with("cloudwatch")
    mock_cloudwatch.put_metric_data.assert_called()

    captured = capsys.readouterr()
    assert "=== Resource Type Level Alarm Metrics ===" in captured.out
    assert "Resource Type: Lambda" in captured.out
    assert "Alarms in ALARM state: 0" in captured.out
