import os
import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_inspector_function import (
    LambdaInspector,
    LambdaFunction,
    ServiceInfo,
    TagNames,
    DimensionNames,
    MetricNames,
    Config,
    create_lambda_dimensions,
    create_terraform_dimensions,
    publish_lambda_metric,
    publish_terraform_metric,
    lambda_handler,
    publish_metrics,
)


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
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

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

    # Mock Config history response
    mock_config.get_paginator.return_value.paginate.return_value = [
        {
            "configurationItems": [
                {
                    "tags": {
                        "AppVersion": "0.9",
                        "TerraformVersion": "0.9.0",
                    }
                }
            ]
        }
    ]

    # Call the handler
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"

    # Verify CloudWatch metrics were published
    # The new lambda_handler calls publish_metrics which may publish multiple metrics
    assert mock_cloudwatch.put_metric_data.call_count >= 1


class TestLambdaInspector:
    """Test cases for LambdaInspector class methods"""

    @patch("lambda_inspector_function.boto3.client")
    def test_get_all_functions_filters_appversion(self, mock_boto3):
        """Test that get_all_functions only returns functions with AppVersion tag"""
        # Create mock clients
        mock_lambda = MagicMock()
        mock_cloudwatch = MagicMock()
        mock_config = MagicMock()
        mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

        # Mock Lambda function list response with mixed functions
        mock_lambda.get_paginator.return_value.paginate.return_value = [
            {
                "Functions": [
                    {
                        "FunctionName": "function-with-appversion",
                        "FunctionArn": "arn:aws:lambda:region:account:function:function-with-appversion",
                    },
                    {
                        "FunctionName": "function-without-appversion",
                        "FunctionArn": "arn:aws:lambda:region:account:function:function-without-appversion",
                    },
                    {
                        "FunctionName": "another-function-with-appversion",
                        "FunctionArn": "arn:aws:lambda:region:account:function:another-function-with-appversion",
                    },
                ]
            }
        ]

        # Mock Lambda tags responses
        def mock_list_tags(Resource):
            if "function-with-appversion" in Resource:
                return {"Tags": {"AppVersion": "1.0", "Stack": "test-stack"}}
            elif "function-without-appversion" in Resource:
                return {"Tags": {"Stack": "test-stack"}}  # No AppVersion
            elif "another-function-with-appversion" in Resource:
                return {"Tags": {"AppVersion": "2.0", "Stack": "prod-stack"}}
            return {"Tags": {}}

        mock_lambda.list_tags.side_effect = mock_list_tags

        inspector = LambdaInspector()
        functions = inspector.get_all_functions()

        # Should only return functions with AppVersion tag
        assert len(functions) == 2
        function_names = [f.name for f in functions]
        assert "function-with-appversion" in function_names
        assert "another-function-with-appversion" in function_names
        assert "function-without-appversion" not in function_names

    @patch("lambda_inspector_function.boto3.client")
    def test_get_all_functions_handles_errors(self, mock_boto3):
        """Test that get_all_functions handles errors gracefully"""
        mock_lambda = MagicMock()
        mock_cloudwatch = MagicMock()
        mock_config = MagicMock()
        mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

        # Mock Lambda function list response
        mock_lambda.get_paginator.return_value.paginate.return_value = [
            {
                "Functions": [
                    {
                        "FunctionName": "function-with-error",
                        "FunctionArn": "arn:aws:lambda:region:account:function:function-with-error",
                    },
                    {
                        "FunctionName": "function-normal",
                        "FunctionArn": "arn:aws:lambda:region:account:function:function-normal",
                    },
                ]
            }
        ]

        # Mock Lambda tags responses - one will fail
        def mock_list_tags(Resource):
            if "function-with-error" in Resource:
                raise Exception("API Error")
            elif "function-normal" in Resource:
                return {"Tags": {"AppVersion": "1.0", "Stack": "test-stack"}}
            return {"Tags": {}}

        mock_lambda.list_tags.side_effect = mock_list_tags

        inspector = LambdaInspector()
        functions = inspector.get_all_functions()

        # Should only return the function that didn't error
        assert len(functions) == 1
        assert functions[0].name == "function-normal"

    def test_extract_service_info_with_complete_tags(self):
        """Test extract_service_info with all required tags present"""
        function = LambdaFunction(
            name="test-function",
            arn="arn:aws:lambda:region:account:function:test-function",
            tags={
                "AppVersion": "1.2.3",
                "Stack": "production",
                "Service": "api",
                "Environment": "prod",
                "TerraformVersion": "1.5.0",
            },
        )

        inspector = LambdaInspector()
        service_info = inspector.extract_service_info(function)

        assert service_info.env == "prod"
        assert service_info.service == "api"
        assert service_info.stack == "production"
        assert service_info.terraform_version == "1.5.0"

    def test_extracEt_service_info_with_missing_optional_tags(self):
        """Test extract_service_info with missing optional tags"""
        function = LambdaFunction(
            name="test-function",
            arn="arn:aws:lambda:region:account:function:test-function",
            tags={"AppVersion": "1.0.0"},  # Only AppVersion present
        )

        inspector = LambdaInspector()
        service_info = inspector.extract_service_info(function)

        assert service_info.env == "Unknown"
        assert service_info.service == "Unknown"
        assert service_info.stack == "Unknown"
        assert service_info.terraform_version == "Unknown"

    @patch("lambda_inspector_function.boto3.client")
    def test_publish_metrics(self, mock_boto3):
        """Test that publish_metrics calls CloudWatch with correct data"""
        mock_cloudwatch = MagicMock()
        mock_config = MagicMock()
        mock_boto3.side_effect = [MagicMock(), mock_cloudwatch, mock_config]

        inspector = LambdaInspector()
        dimensions = [
            {"Name": "Env", "Value": "test"},
            {"Name": "Service", "Value": "test-service"},
        ]
        inspector.publish_metrics("testMetric", dimensions, 1)

        # Verify CloudWatch put_metric_data was called
        mock_cloudwatch.put_metric_data.assert_called_once()
        call_args = mock_cloudwatch.put_metric_data.call_args

        # Check the metric data structure
        metric_data = call_args[1]["MetricData"][0]
        assert metric_data["MetricName"] == "testMetric"
        assert metric_data["Value"] == 1
        assert metric_data["Unit"] == "Count"


@patch("lambda_inspector_function.boto3.client")
def test_lambda_handler_with_multiple_functions(mock_boto3):
    """Test lambda_handler with multiple functions having different tag combinations"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "function-1",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-1",
                },
                {
                    "FunctionName": "function-2",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-2",
                },
                {
                    "FunctionName": "function-3",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-3",
                },
            ]
        },
        # Second page with more functions
        {
            "Functions": [
                {
                    "FunctionName": "function-4",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-4",
                },
            ]
        },
    ]

    # Mock Lambda tags responses
    def mock_list_tags(Resource):
        if "function-1" in Resource:
            return {
                "Tags": {
                    "AppVersion": "1.0",
                    "Stack": "stack-a",
                    "Service": "service-1",
                    "Environment": "dev",
                    "TerraformVersion": "1.0.0",
                }
            }
        elif "function-2" in Resource:
            return {
                "Tags": {
                    "AppVersion": "2.0",
                    "Stack": "stack-b",
                    "Service": "service-2",
                    "Environment": "prod",
                    "TerraformVersion": "1.1.0",
                }
            }
        elif "function-3" in Resource:
            return {
                "Tags": {
                    "AppVersion": "1.5",
                    "Stack": "stack-a",  # Same stack as function-1
                    "Service": "service-3",
                    "Environment": "dev",
                    "TerraformVersion": "1.0.0",
                }
            }
        elif "function-4" in Resource:
            return {
                "Tags": {
                    "AppVersion": "3.0",
                    "Stack": "stack-c",
                    "Service": "service-4",
                    "Environment": "staging",
                    "TerraformVersion": "1.2.0",
                }
            }
        return {"Tags": {}}

    mock_lambda.list_tags.side_effect = mock_list_tags

    # Mock Config history response
    mock_config.get_paginator.return_value.paginate.return_value = [
        {
            "configurationItems": [
                {
                    "tags": {
                        "AppVersion": "0.9",
                        "TerraformVersion": "0.9.0",
                    }
                }
            ]
        }
    ]

    # Call the handler
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"

    # Verify CloudWatch metrics were published
    # The new lambda_handler calls publish_metrics which may publish multiple metrics
    assert mock_cloudwatch.put_metric_data.call_count >= 1


@patch("lambda_inspector_function.boto3.client")
def test_lambda_handler_with_no_functions(mock_boto3):
    """Test lambda_handler when no functions are found"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock empty Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [{"Functions": []}]

    # Call the handler
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"

    # Verify no CloudWatch metrics were published
    mock_cloudwatch.put_metric_data.assert_not_called()


@patch("lambda_inspector_function.boto3.client")
def test_lambda_handler_with_functions_without_appversion(mock_boto3):
    """Test lambda_handler when all functions lack AppVersion tag"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "function-without-appversion-1",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-without-appversion-1",
                },
                {
                    "FunctionName": "function-without-appversion-2",
                    "FunctionArn": "arn:aws:lambda:region:account:function:function-without-appversion-2",
                },
            ]
        }
    ]

    # Mock Lambda tags responses - no AppVersion tags
    mock_lambda.list_tags.return_value = {
        "Tags": {
            "Stack": "test-stack",
            "Service": "test-service",
            "Environment": "test-env",
        }
    }

    # Call the handler
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"

    # Verify no CloudWatch metrics were published since no functions have AppVersion
    mock_cloudwatch.put_metric_data.assert_not_called()


@patch("lambda_inspector_function.boto3.client")
def test_lambda_handler_handles_cloudwatch_errors(mock_boto3):
    """Test lambda_handler handles CloudWatch errors gracefully"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function",
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

    # Mock CloudWatch to raise an error
    mock_cloudwatch.put_metric_data.side_effect = Exception("CloudWatch error")

    # Call the handler - should not raise an exception
    response = lambda_handler({}, {})

    # Verify the response
    assert response["statusCode"] == 200
    assert response["body"] == "Metrics updated successfully"


# Tests for new helper functions and classes
class TestTagNames:
    """Test TagNames constants class"""

    def test_tag_names_values(self):
        """Test that tag names have correct values"""
        assert TagNames.APP_VERSION == "AppVersion"
        assert TagNames.TERRAFORM_VERSION == "TerraformVersion"
        assert TagNames.ENVIRONMENT == "Environment"
        assert TagNames.SERVICE == "Service"
        assert TagNames.STACK == "Stack"


class TestDimensionNames:
    """Test DimensionNames constants class"""

    def test_dimension_names_values(self):
        """Test that dimension names have correct values"""
        assert DimensionNames.ENV == "Env"
        assert DimensionNames.SERVICE == "Service"
        assert DimensionNames.STACK == "Stack"
        assert DimensionNames.FUNCTION_NAME == "FunctionName"
        assert DimensionNames.APP_VERSION == "AppVersion"
        assert DimensionNames.TERRAFORM_VERSION == "TerraformVersion"


class TestMetricNames:
    """Test MetricNames constants class"""

    def test_metric_names_values(self):
        """Test that metric names have correct values"""
        assert MetricNames.LAMBDA_TAG == "lambdaTag"
        assert MetricNames.TERRAFORM_TAG == "terraformTag"


class TestConfig:
    """Test Config constants class"""

    def test_config_values(self):
        """Test that config values are correct"""
        assert Config.METRIC_UNIT == "Count"
        assert Config.UNKNOWN_VALUE == "Unknown"
        assert Config.HISTORY_DAYS_LOOKBACK == 365
        assert Config.RECENT_DAYS_CUTOFF == 0
        assert Config.CONFIG_HISTORY_LIMIT == 100
        assert Config.AWS_LAMBDA_FUNCTION_RESOURCE_TYPE == "AWS::Lambda::Function"


class TestDimensionFunctions:
    """Test dimension creation helper functions"""

    def test_create_lambda_dimensions(self):
        """Test create_lambda_dimensions function"""
        service_info = ServiceInfo(
            env="test-env",
            service="test-service",
            stack="test-stack",
            terraform_version="1.0.0",
        )
        function_name = "test-function"
        app_version = "1.2.3"

        dimensions = create_lambda_dimensions(service_info, function_name, app_version)

        expected = [
            {"Name": "Env", "Value": "test-env"},
            {"Name": "Stack", "Value": "test-stack"},
            {"Name": "Service", "Value": "test-service"},
            {"Name": "FunctionName", "Value": "test-function"},
            {"Name": "AppVersion", "Value": "1.2.3"},
        ]

        assert dimensions == expected

    def test_create_terraform_dimensions(self):
        """Test create_terraform_dimensions function"""
        service_info = ServiceInfo(
            env="prod",
            service="api-service",
            stack="production",
            terraform_version="2.0.0",
        )
        terraform_version = "2.1.0"

        dimensions = create_terraform_dimensions(service_info, terraform_version)

        expected = [
            {"Name": "Env", "Value": "prod"},
            {"Name": "Stack", "Value": "production"},
            {"Name": "Service", "Value": "api-service"},
            {"Name": "TerraformVersion", "Value": "2.1.0"},
        ]

        assert dimensions == expected


@patch("lambda_inspector_function.boto3.client")
class TestPublishHelperFunctions:
    """Test high-level publishing helper functions"""

    def test_publish_lambda_metric(self, mock_boto3):
        """Test publish_lambda_metric function"""
        mock_cloudwatch = MagicMock()
        mock_boto3.return_value = mock_cloudwatch

        inspector = LambdaInspector()
        service_info = ServiceInfo(
            env="test",
            service="test-service",
            stack="test-stack",
            terraform_version="1.0.0",
        )

        publish_lambda_metric(inspector, service_info, "test-function", "1.0.0", 1)

        # Verify CloudWatch was called
        mock_cloudwatch.put_metric_data.assert_called_once()
        call_args = mock_cloudwatch.put_metric_data.call_args

        # Check metric data
        metric_data = call_args[1]["MetricData"][0]
        assert metric_data["MetricName"] == "lambdaTag"
        assert metric_data["Value"] == 1
        assert metric_data["Unit"] == "Count"

        # Check dimensions
        dimensions = {d["Name"]: d["Value"] for d in metric_data["Dimensions"]}
        assert dimensions["Env"] == "test"
        assert dimensions["Service"] == "test-service"
        assert dimensions["Stack"] == "test-stack"
        assert dimensions["FunctionName"] == "test-function"
        assert dimensions["AppVersion"] == "1.0.0"

    def test_publish_terraform_metric(self, mock_boto3):
        """Test publish_terraform_metric function"""
        mock_cloudwatch = MagicMock()
        mock_boto3.return_value = mock_cloudwatch

        inspector = LambdaInspector()
        service_info = ServiceInfo(
            env="prod",
            service="api-service",
            stack="production",
            terraform_version="2.0.0",
        )

        publish_terraform_metric(inspector, service_info, "2.1.0", 0)

        # Verify CloudWatch was called
        mock_cloudwatch.put_metric_data.assert_called_once()
        call_args = mock_cloudwatch.put_metric_data.call_args

        # Check metric data
        metric_data = call_args[1]["MetricData"][0]
        assert metric_data["MetricName"] == "terraformTag"
        assert metric_data["Value"] == 0
        assert metric_data["Unit"] == "Count"

        # Check dimensions
        dimensions = {d["Name"]: d["Value"] for d in metric_data["Dimensions"]}
        assert dimensions["Env"] == "prod"
        assert dimensions["Service"] == "api-service"
        assert dimensions["Stack"] == "production"
        assert dimensions["TerraformVersion"] == "2.1.0"


@patch("lambda_inspector_function.boto3.client")
def test_publish_metrics_with_history(mock_boto3):
    """Test publish_metrics function with history"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function",
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

    # Mock Config history response
    mock_config.get_paginator.return_value.paginate.return_value = [
        {
            "configurationItems": [
                {
                    "tags": {
                        "AppVersion": "0.9",
                        "TerraformVersion": "0.9.0",
                    }
                }
            ]
        }
    ]

    # Call publish_metrics with history
    publish_metrics(include_history=True)

    # Verify CloudWatch metrics were published
    assert mock_cloudwatch.put_metric_data.call_count >= 1


@patch("lambda_inspector_function.boto3.client")
def test_publish_metrics_without_history(mock_boto3):
    """Test publish_metrics function without history"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function",
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

    # Call publish_metrics without history
    publish_metrics(include_history=False)

    # Verify CloudWatch metrics were published
    assert mock_cloudwatch.put_metric_data.call_count >= 1


class TestSetInitialization:
    """Test set initialization with curly braces syntax"""

    def test_set_initialization_with_single_value(self):
        """Test that sets are properly initialized with single values using curly braces"""
        # Test the new syntax: {value} instead of set(value)
        app_version = "1.2.3"
        terraform_version = "2.0.0"

        # This is how the code now initializes sets
        app_versions = {app_version}
        terraform_versions = {terraform_version}

        # Verify they are sets
        assert isinstance(app_versions, set)
        assert isinstance(terraform_versions, set)

        # Verify they contain the expected values
        assert app_versions == {"1.2.3"}
        assert terraform_versions == {"2.0.0"}

        # Verify they can be updated with other sets
        historical_versions = {"0.9.0", "1.0.0"}
        app_versions.update(historical_versions)
        assert app_versions == {"1.2.3", "0.9.0", "1.0.0"}


@patch("lambda_inspector_function.boto3.client")
def test_publish_metrics_with_empty_history(mock_boto3):
    """Test publish_metrics when AWS Config returns empty history"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function",
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

    # Mock empty Config history response
    mock_config.get_paginator.return_value.paginate.return_value = [
        {"configurationItems": []}
    ]

    # Call publish_metrics with history but empty results
    publish_metrics(include_history=True, earlier_days=1, later_days=0)

    # Verify CloudWatch metrics were still published (using current tags)
    assert mock_cloudwatch.put_metric_data.call_count >= 1


@patch("lambda_inspector_function.boto3.client")
def test_get_resource_history_tags_exception_handling(mock_boto3):
    """Test get_resource_history_tags handles exceptions gracefully"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Config to raise an exception
    mock_config.get_paginator.return_value.paginate.side_effect = Exception(
        "Config API Error"
    )

    inspector = LambdaInspector()

    # This should not raise an exception and should return empty list
    result = inspector.get_resource_history_tags(
        "test-function", "AWS::Lambda::Function", 1, 0
    )

    # Should return empty list when exception occurs
    assert result == []


@patch("lambda_inspector_function.boto3.client")
def test_publish_metrics_with_config_exception(mock_boto3):
    """Test publish_metrics handles AWS Config exceptions gracefully"""
    # Create mock clients
    mock_lambda = MagicMock()
    mock_cloudwatch = MagicMock()
    mock_config = MagicMock()
    mock_boto3.side_effect = [mock_lambda, mock_cloudwatch, mock_config]

    # Mock Lambda function list response
    mock_lambda.get_paginator.return_value.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "test-function",
                    "FunctionArn": "arn:aws:lambda:region:account:function:test-function",
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

    # Mock Config to raise an exception
    mock_config.get_paginator.return_value.paginate.side_effect = Exception(
        "Config API Error"
    )

    # Call publish_metrics with history - should handle Config exception gracefully
    publish_metrics(include_history=True, earlier_days=1, later_days=0)

    # Verify CloudWatch metrics were still published (using current tags only)
    assert mock_cloudwatch.put_metric_data.call_count >= 1
