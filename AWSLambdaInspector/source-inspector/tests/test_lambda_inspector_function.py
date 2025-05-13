import os
import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_inspector_function import lambda_handler


@pytest.fixture
def mock_cloudwatch():
    mock = MagicMock()
    mock.get_paginator.return_value = MagicMock()
    return mock


@patch("lambda_inspector_function.boto3.client")
def test_lambda_handler(mock_boto3):
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function-1",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function-1",
                }
            ]
        }
    ]

    # Mock Lambda tags response
    mock_lambda.list_tags.return_value = {
        "Tags": {
            "AppVersion": "1.0",
            "Stack": "test-stack",
            "Service": "test-service",
            "Environment": "test-env",
            "TerraformVersion": "1.0.0",
        }
    }

    # Call the handler
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"

    # Verify CloudWatch metrics were published
    assert (
        mock_cloudwatch.put_metric_data.call_count == 2
    )  # One for lambdaTag, one for terraformTag
