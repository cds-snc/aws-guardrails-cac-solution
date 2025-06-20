"""
Unit tests for aws_lambda_permissions_setup Lambda function.
Tests cover account retrieval, permission management, CloudFormation responses, and Lambda handler.
"""

import json
import os
import pytest
from unittest import mock
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
import urllib3

import app


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """Set up environment variables for all tests."""
    monkeypatch.setenv("OrganizationName", "testorg-")
    monkeypatch.setenv("ORG_ID", "o-1234567890")


@pytest.fixture
def sample_accounts():
    """Sample AWS accounts for testing."""
    return [
        {"Id": "123456789012", "Status": "ACTIVE", "Name": "Account1"},
        {"Id": "123456789013", "Status": "ACTIVE", "Name": "Account2"},
        {"Id": "123456789014", "Status": "SUSPENDED", "Name": "Account3"},
    ]


@pytest.fixture
def sample_lambda_event():
    """Sample CloudFormation event for testing."""
    return {
        "RequestType": "Create",
        "ResponseURL": "https://example.com/response",
        "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/test/123",
        "RequestId": "unique-id",
        "LogicalResourceId": "TestResource",
        "PhysicalResourceId": "test-resource-id",
    }


@pytest.fixture
def mock_context():
    """Mock Lambda context object."""
    context = Mock()
    context.log_stream_name = "test-log-stream"
    return context


class TestGetAccounts:
    """Test cases for get_accounts function."""

    @patch("boto3.client")
    def test_get_accounts_success(self, mock_boto_client, sample_accounts):
        """Test successful account retrieval."""
        mock_org_client = Mock()
        mock_org_client.list_accounts.return_value = {
            "Accounts": sample_accounts,
            "NextToken": None,
        }
        mock_boto_client.return_value = mock_org_client

        result = app.get_accounts()

        assert result == sample_accounts
        mock_boto_client.assert_called_with("organizations")
        mock_org_client.list_accounts.assert_called_once()

    @patch("boto3.client")
    def test_get_accounts_with_pagination(self, mock_boto_client, sample_accounts):
        """Test account retrieval with pagination."""
        mock_org_client = Mock()
        # First call returns partial results with NextToken
        mock_org_client.list_accounts.side_effect = [
            {"Accounts": sample_accounts[:2], "NextToken": "token123"},
            {"Accounts": sample_accounts[2:], "NextToken": None},
        ]
        mock_boto_client.return_value = mock_org_client

        result = app.get_accounts()

        assert len(result) == 3
        assert result == sample_accounts
        assert mock_org_client.list_accounts.call_count == 2

    @patch("boto3.client")
    def test_get_accounts_too_many_requests(self, mock_boto_client):
        """Test account retrieval with throttling."""
        mock_org_client = Mock()
        # First call raises TooManyRequestsException, second succeeds
        mock_org_client.list_accounts.side_effect = [
            ClientError(
                {
                    "Error": {
                        "Code": "TooManyRequestsException",
                        "Message": "Rate exceeded",
                    }
                },
                "ListAccounts",
            ),
            {"Accounts": [], "NextToken": None},
        ]
        mock_boto_client.return_value = mock_org_client

        with patch("time.sleep"):
            result = app.get_accounts()

        assert result == []
        assert mock_org_client.list_accounts.call_count == 2

    @patch("boto3.client")
    def test_get_accounts_access_denied(self, mock_boto_client):
        """Test account retrieval with access denied error."""
        mock_org_client = Mock()
        mock_org_client.list_accounts.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
            "ListAccounts",
        )
        mock_boto_client.return_value = mock_org_client

        result = app.get_accounts()

        assert result == []

    @patch("boto3.client")
    def test_get_accounts_empty_response(self, mock_boto_client):
        """Test account retrieval with empty response."""
        mock_org_client = Mock()
        mock_org_client.list_accounts.return_value = None
        mock_boto_client.return_value = mock_org_client

        result = app.get_accounts()

        assert result == []


class TestApplyLambdaPermissions:
    """Test cases for apply_lambda_permissions function."""

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_success(
        self, mock_boto_client, mock_get_accounts, sample_accounts
    ):
        """Test successful permission application."""
        # Mock accounts
        mock_get_accounts.return_value = sample_accounts

        # Mock Lambda client
        mock_lambda_client = Mock()
        mock_lambda_client.get_policy.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetPolicy"
        )
        mock_lambda_client.add_permission.return_value = {"Statement": "test-statement"}
        mock_boto_client.return_value = mock_lambda_client

        result = app.apply_lambda_permissions()

        assert result == 1
        # Should be called for each lambda function
        assert mock_lambda_client.add_permission.call_count > 0

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_with_existing_policy(
        self, mock_boto_client, mock_get_accounts, sample_accounts
    ):
        """Test permission application with existing policy."""
        mock_get_accounts.return_value = sample_accounts

        # Mock existing policy
        existing_policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "config.amazonaws.com"},
                    "Action": "lambda:InvokeFunction",
                    "Condition": {
                        "StringEquals": {"AWS:SourceAccount": "123456789012"}
                    },
                    "Sid": "ExistingSid",
                }
            ]
        }

        mock_lambda_client = Mock()
        mock_lambda_client.get_policy.return_value = {
            "Policy": json.dumps(existing_policy)
        }
        mock_lambda_client.add_permission.return_value = {"Statement": "test-statement"}
        mock_boto_client.return_value = mock_lambda_client

        result = app.apply_lambda_permissions()

        assert result == 1
        # Should still add permissions for accounts not in existing policy
        assert mock_lambda_client.add_permission.call_count > 0

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_no_accounts(
        self, mock_boto_client, mock_get_accounts
    ):
        """Test permission application with no accounts."""
        mock_get_accounts.return_value = []

        result = app.apply_lambda_permissions()

        assert result == 0

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_add_permission_error(
        self, mock_boto_client, mock_get_accounts, sample_accounts
    ):
        """Test permission application with add_permission error."""
        mock_get_accounts.return_value = sample_accounts

        mock_lambda_client = Mock()
        mock_lambda_client.get_policy.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetPolicy"
        )
        mock_lambda_client.add_permission.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
            "AddPermission",
        )
        mock_boto_client.return_value = mock_lambda_client

        result = app.apply_lambda_permissions()

        assert result == -1

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_invalid_response(
        self, mock_boto_client, mock_get_accounts, sample_accounts
    ):
        """Test permission application with invalid response."""
        mock_get_accounts.return_value = sample_accounts

        mock_lambda_client = Mock()
        mock_lambda_client.get_policy.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetPolicy"
        )
        mock_lambda_client.add_permission.return_value = {}  # No 'Statement' key
        mock_boto_client.return_value = mock_lambda_client

        result = app.apply_lambda_permissions()

        assert result == -1

    @patch("app.get_accounts")
    @patch("boto3.client")
    def test_apply_lambda_permissions_throttling(
        self, mock_boto_client, mock_get_accounts, sample_accounts
    ):
        """Test permission application with throttling."""
        mock_get_accounts.return_value = sample_accounts[
            :1
        ]  # Only one account to simplify

        mock_lambda_client = Mock()
        mock_lambda_client.get_policy.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetPolicy"
        )

        # Create a cycle of responses: throttle once, then succeed for all subsequent calls
        throttle_error = ClientError(
            {"Error": {"Code": "TooManyRequestsException"}}, "AddPermission"
        )
        success_response = {"Statement": "test-statement"}

        def add_permission_side_effect(*args, **kwargs):
            # First call raises throttle error, all subsequent calls succeed
            if not hasattr(add_permission_side_effect, "call_count"):
                add_permission_side_effect.call_count = 0
            add_permission_side_effect.call_count += 1

            if add_permission_side_effect.call_count == 1:
                raise throttle_error
            return success_response

        mock_lambda_client.add_permission.side_effect = add_permission_side_effect
        mock_boto_client.return_value = mock_lambda_client

        with patch("time.sleep"):
            result = app.apply_lambda_permissions()

        assert result == 1


class TestSendFunction:
    """Test cases for send function."""

    @patch("app.http")
    def test_send_success_response(self, mock_http, sample_lambda_event, mock_context):
        """Test successful CloudFormation response."""
        mock_response = Mock()
        mock_response.status = 200
        mock_http.request.return_value = mock_response

        app.send(sample_lambda_event, mock_context, app.SUCCESS, {"test": "data"})

        mock_http.request.assert_called_once()
        call_args = mock_http.request.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == sample_lambda_event["ResponseURL"]

    @patch("app.http")
    def test_send_failure_response(self, mock_http, sample_lambda_event, mock_context):
        """Test failure CloudFormation response."""
        mock_response = Mock()
        mock_response.status = 200
        mock_http.request.return_value = mock_response

        app.send(
            sample_lambda_event, mock_context, app.FAILED, {}, reason="Test failure"
        )

        mock_http.request.assert_called_once()
        call_args = mock_http.request.call_args
        request_body = json.loads(call_args[1]["body"])
        assert request_body["Status"] == app.FAILED
        assert request_body["Reason"] == "Test failure"

    @patch("app.http")
    def test_send_http_error(self, mock_http, sample_lambda_event, mock_context):
        """Test send function with HTTP error."""
        mock_http.request.side_effect = urllib3.exceptions.HTTPError("Connection error")

        # Should not raise exception
        app.send(sample_lambda_event, mock_context, app.SUCCESS, {})


class TestLambdaHandler:
    """Test cases for lambda_handler function."""

    @patch("app.apply_lambda_permissions")
    @patch("app.send")
    def test_lambda_handler_create_success(
        self, mock_send, mock_apply_permissions, sample_lambda_event, mock_context
    ):
        """Test Lambda handler for successful Create request."""
        mock_apply_permissions.return_value = 1
        sample_lambda_event["RequestType"] = "Create"

        app.lambda_handler(sample_lambda_event, mock_context)

        mock_apply_permissions.assert_called_once()
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[2] == app.SUCCESS  # response_status

    @patch("app.apply_lambda_permissions")
    @patch("app.send")
    def test_lambda_handler_create_failure(
        self, mock_send, mock_apply_permissions, sample_lambda_event, mock_context
    ):
        """Test Lambda handler for failed Create request."""
        mock_apply_permissions.return_value = -1
        sample_lambda_event["RequestType"] = "Create"

        app.lambda_handler(sample_lambda_event, mock_context)

        mock_apply_permissions.assert_called_once()
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[2] == app.FAILED  # response_status

    @patch("app.apply_lambda_permissions")
    @patch("app.send")
    def test_lambda_handler_update_success(
        self, mock_send, mock_apply_permissions, sample_lambda_event, mock_context
    ):
        """Test Lambda handler for successful Update request."""
        mock_apply_permissions.return_value = 1
        sample_lambda_event["RequestType"] = "Update"

        app.lambda_handler(sample_lambda_event, mock_context)

        mock_apply_permissions.assert_called_once()
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[2] == app.SUCCESS

    @patch("app.send")
    def test_lambda_handler_delete(self, mock_send, sample_lambda_event, mock_context):
        """Test Lambda handler for Delete request."""
        sample_lambda_event["RequestType"] = "Delete"

        app.lambda_handler(sample_lambda_event, mock_context)

        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[2] == app.SUCCESS

    @patch("app.apply_lambda_permissions")
    def test_lambda_handler_cron(
        self, mock_apply_permissions, sample_lambda_event, mock_context
    ):
        """Test Lambda handler for Cron request."""
        mock_apply_permissions.return_value = 1
        sample_lambda_event["RequestType"] = "Cron"

        result = app.lambda_handler(sample_lambda_event, mock_context)

        mock_apply_permissions.assert_called_once()
        # Cron doesn't send CloudFormation response

    @patch("app.send")
    def test_lambda_handler_unknown_request_type(
        self, mock_send, sample_lambda_event, mock_context
    ):
        """Test Lambda handler for unknown request type."""
        sample_lambda_event["RequestType"] = "Unknown"

        app.lambda_handler(sample_lambda_event, mock_context)

        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[2] == app.FAILED
