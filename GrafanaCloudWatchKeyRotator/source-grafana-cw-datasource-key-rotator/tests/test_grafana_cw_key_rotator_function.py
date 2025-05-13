import pytest
import boto3
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create mock objects
_mock_iam = MagicMock()
_mock_secretsmanager = MagicMock()


# Create a mock for boto3.client
def mock_boto3_client(*args, **kwargs):
    if args[0] == "iam":
        return _mock_iam
    elif args[0] == "secretsmanager":
        return _mock_secretsmanager
    return MagicMock()


# Patch boto3.client before importing the module
with patch("boto3.client", side_effect=mock_boto3_client):
    from grafana_cw_key_rotator_function import (
        get_grafana_api_key,
        update_grafana_datasource,
        rotate_access_key,
        lambda_handler,
    )


# Fixtures
@pytest.fixture(autouse=True)
def setup_mocks():
    _mock_iam.reset_mock()
    _mock_secretsmanager.reset_mock()
    _mock_iam.side_effect = None
    _mock_iam.return_value = None
    _mock_secretsmanager.side_effect = None
    _mock_secretsmanager.return_value = None
    # Also clear method-level side_effects/return_values
    if hasattr(_mock_secretsmanager, "get_secret_value"):
        _mock_secretsmanager.get_secret_value.side_effect = None
        _mock_secretsmanager.get_secret_value.return_value = None
    if hasattr(_mock_iam, "list_access_keys"):
        _mock_iam.list_access_keys.side_effect = None
        _mock_iam.list_access_keys.return_value = None
    yield


@pytest.fixture
def mock_secretsmanager():
    return _mock_secretsmanager


@pytest.fixture
def mock_iam():
    return _mock_iam


@pytest.fixture
def mock_requests():
    with patch("requests.get") as mock_get, patch("requests.put") as mock_put:
        yield mock_get, mock_put


@pytest.fixture
def mock_env_vars():
    env_vars = {
        "GRAFANA_API_KEY_PATH": "test/api/key/path",
        "GRAFANA_URL": "http://test.grafana.com",
        "AWS_REGION": "us-west-2",
        "ROTATION_PERIOD": "30",
        "IAM_USERNAME": "test-user",
        "GRAFANA_DATASOURCE_NAME": "CloudWatch",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


# Test get_grafana_api_key
def test_get_grafana_api_key_success(mock_secretsmanager, mock_env_vars):
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({"apikey": "test-api-key"})
    }

    result = get_grafana_api_key()
    assert result == "test-api-key"
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="test/api/key/path"
    )


def test_get_grafana_api_key_error(mock_secretsmanager, mock_env_vars):
    mock_secretsmanager.get_secret_value.side_effect = Exception("Test error")

    with pytest.raises(Exception) as exc_info:
        get_grafana_api_key()
    assert str(exc_info.value) == "Test error"


# Test update_grafana_datasource
def test_update_grafana_datasource_success(
    mock_requests, mock_env_vars, mock_secretsmanager
):
    mock_get, mock_put = mock_requests
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({"apikey": "test-api-key"})
    }

    # Mock the get datasources response
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "CloudWatch", "type": "cloudwatch"}
    ]
    mock_get.return_value.raise_for_status = MagicMock()

    # Mock the put update response
    mock_put.return_value.raise_for_status = MagicMock()

    update_grafana_datasource("test-access-key", "test-secret-key", "CloudWatch")

    mock_get.assert_called_once()
    mock_put.assert_called_once()
    update_data = mock_put.call_args[1]["json"]
    assert update_data["name"] == "CloudWatch"
    assert update_data["type"] == "cloudwatch"
    assert update_data["secureJsonData"]["accessKey"] == "test-access-key"
    assert update_data["secureJsonData"]["secretKey"] == "test-secret-key"


def test_update_grafana_datasource_not_found(
    mock_requests, mock_env_vars, mock_secretsmanager
):
    mock_get, mock_put = mock_requests
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({"apikey": "test-api-key"})
    }

    # Mock the get datasources response with no matching datasource
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "Other", "type": "other"}
    ]
    mock_get.return_value.raise_for_status = MagicMock()

    update_grafana_datasource("test-access-key", "test-secret-key", "CloudWatch")

    mock_get.assert_called_once()
    mock_put.assert_not_called()


# Test rotate_access_key
def test_rotate_access_key_new_key(mock_iam, mock_env_vars, mock_secretsmanager):
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({"apikey": "test-api-key"})
    }

    # Mock no existing keys
    mock_iam.list_access_keys.return_value = {"AccessKeyMetadata": []}

    # Mock new key creation
    mock_iam.create_access_key.return_value = {
        "AccessKey": {"AccessKeyId": "new-key-id", "SecretAccessKey": "new-secret-key"}
    }

    with patch(
        "grafana_cw_key_rotator_function.update_grafana_datasource"
    ) as mock_update:
        result = rotate_access_key("test-user", 30, "CloudWatch")

        assert result["statusCode"] == 200
        mock_iam.create_access_key.assert_called_once_with(UserName="test-user")
        mock_update.assert_called_once_with(
            "new-key-id", "new-secret-key", "CloudWatch"
        )


def test_rotate_access_key_rotation(mock_iam, mock_env_vars, mock_secretsmanager):
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({"apikey": "test-api-key"})
    }

    # Mock existing key that needs rotation
    old_date = datetime.now(timezone.utc).replace(year=2020)
    mock_iam.list_access_keys.return_value = {
        "AccessKeyMetadata": [
            {"AccessKeyId": "old-key-id", "CreateDate": old_date, "Status": "Active"}
        ]
    }

    # Mock new key creation
    mock_iam.create_access_key.return_value = {
        "AccessKey": {"AccessKeyId": "new-key-id", "SecretAccessKey": "new-secret-key"}
    }

    with patch(
        "grafana_cw_key_rotator_function.update_grafana_datasource"
    ) as mock_update:
        result = rotate_access_key("test-user", 30, "CloudWatch")

        assert result["statusCode"] == 200
        mock_iam.update_access_key.assert_called_once_with(
            UserName="test-user", AccessKeyId="old-key-id", Status="Inactive"
        )
        mock_iam.delete_access_key.assert_called_once_with(
            UserName="test-user", AccessKeyId="old-key-id"
        )
        mock_iam.create_access_key.assert_called_once_with(UserName="test-user")
        mock_update.assert_called_once_with(
            "new-key-id", "new-secret-key", "CloudWatch"
        )


# Test lambda_handler
def test_lambda_handler_success(mock_env_vars):
    with patch("grafana_cw_key_rotator_function.rotate_access_key") as mock_rotate:
        mock_rotate.return_value = {
            "statusCode": 200,
            "body": "Rotation completed successfully",
        }

        result = lambda_handler({}, {})

        assert result["statusCode"] == 200
        mock_rotate.assert_called_once_with("test-user", 30, "CloudWatch")


def test_lambda_handler_missing_env_vars():
    with patch.dict(os.environ, {}, clear=True):
        result = lambda_handler({}, {})
        assert result["statusCode"] == 400
        assert "IAM_USERNAME environment variable is required" in result["body"]


def test_lambda_handler_error(mock_env_vars):
    with patch("grafana_cw_key_rotator_function.rotate_access_key") as mock_rotate:
        mock_rotate.side_effect = Exception("Test error")

        with pytest.raises(Exception) as exc_info:
            lambda_handler({}, {})
        assert str(exc_info.value) == "Test error"
