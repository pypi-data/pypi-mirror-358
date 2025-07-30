"""Tests for web_utils module."""

import pytest
from unittest.mock import Mock

from quarkle_monitoring.web_utils import (
    extract_error_message,
    build_request_data,
    COMMON_BOT_ENDPOINTS,
    COMMON_BOT_ERROR_CODES,
)


class TestExtractErrorMessage:
    """Test extract_error_message function."""

    def test_extract_from_json_response_with_message(self):
        """Test extracting error message from JSON response with 'message' field."""
        response = Mock()
        response.status_code = 404
        response.is_json.return_value = True
        response.get_json.return_value = {"message": "Resource not found"}

        result = extract_error_message(response)
        assert result == "Resource not found"

    def test_extract_from_json_response_with_error(self):
        """Test extracting error message from JSON response with 'error' field."""
        response = Mock()
        response.status_code = 400
        response.is_json.return_value = True
        response.get_json.return_value = {"error": "Invalid request"}

        result = extract_error_message(response)
        assert result == "Invalid request"

    def test_extract_from_json_response_with_detail(self):
        """Test extracting error message from JSON response with 'detail' field."""
        response = Mock()
        response.status_code = 422
        response.is_json.return_value = True
        response.get_json.return_value = {"detail": "Validation failed"}

        result = extract_error_message(response)
        assert result == "Validation failed"

    def test_extract_from_json_response_fallback_to_str(self):
        """Test fallback to str(data) when no standard fields present."""
        response = Mock()
        response.status_code = 500
        response.is_json.return_value = True
        response.get_json.return_value = {"custom_field": "Some error"}

        result = extract_error_message(response)
        assert result == "{'custom_field': 'Some error'}"

    def test_extract_from_text_response(self):
        """Test extracting error message from text response."""
        response = Mock()
        response.status_code = 404
        response.is_json.return_value = False
        response.get_data.return_value = "Page not found"

        result = extract_error_message(response)
        assert result == "Page not found"

    def test_extract_from_long_text_response(self):
        """Test that long text responses are ignored."""
        response = Mock()
        response.status_code = 500
        response.is_json.return_value = False
        response.get_data.return_value = "A" * 600  # Longer than max_length

        result = extract_error_message(response)
        assert result == "HTTP 500 error"

    def test_extract_with_no_data(self):
        """Test extraction when response has no data."""
        response = Mock()
        response.status_code = 404
        response.is_json.return_value = True
        response.get_json.return_value = None

        result = extract_error_message(response)
        assert result == "HTTP 404 error"

    def test_extract_with_exception(self):
        """Test extraction when get_json() raises exception."""
        response = Mock()
        response.status_code = 500
        response.is_json.return_value = True
        response.get_json.side_effect = Exception("Parse error")

        result = extract_error_message(response)
        assert result == "HTTP 500 error"

    def test_extract_without_json_support(self):
        """Test extraction from response without JSON support."""
        response = Mock()
        response.status_code = 404
        # No is_json attribute
        del response.is_json
        response.get_data.return_value = "Not found"

        result = extract_error_message(response)
        assert result == "Not found"


class TestBuildRequestData:
    """Test build_request_data function."""

    def test_basic_get_request(self):
        """Test building data for basic GET request."""
        request = Mock()
        request.method = "GET"
        request.args = {"param1": "value1", "param2": "value2"}

        result = build_request_data(request, "/api/users")

        expected = {
            "method": "GET",
            "path": "/api/users",
            "query_params": {"param1": "value1", "param2": "value2"},
        }
        assert result == expected

    def test_get_request_no_args(self):
        """Test GET request without query parameters."""
        request = Mock()
        request.method = "GET"
        request.args = None

        result = build_request_data(request, "/api/users")

        expected = {"method": "GET", "path": "/api/users", "query_params": None}
        assert result == expected

    def test_post_request_with_json(self):
        """Test POST request with JSON data."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = True
        request.content_length = 100
        request.get_json.return_value = {"name": "test", "email": "test@example.com"}

        result = build_request_data(request, "/api/users")

        assert result["method"] == "POST"
        assert result["path"] == "/api/users"
        assert "json_data" in result
        assert "'name': 'test'" in result["json_data"]

    def test_post_request_with_form_data(self):
        """Test POST request with form data."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = False
        request.form = {"username": "testuser", "password": "secret"}

        result = build_request_data(request, "/api/login")

        assert result["method"] == "POST"
        assert result["path"] == "/api/login"
        assert "form_data" in result
        assert "'username': 'testuser'" in result["form_data"]

    def test_post_request_large_json_ignored(self):
        """Test that large JSON payloads are ignored."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = True
        request.content_length = 2000  # Larger than max_body_size

        result = build_request_data(request, "/api/upload")

        assert result["method"] == "POST"
        assert "json_data" not in result

    def test_post_request_large_form_ignored(self):
        """Test that large form data is ignored."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = False
        # Create large form data
        large_form = {f"field_{i}": f"value_{i}" for i in range(100)}
        request.form = large_form

        result = build_request_data(request, "/api/upload")

        assert result["method"] == "POST"
        assert "form_data" not in result

    def test_post_request_json_truncated(self):
        """Test that JSON data is truncated to max_field_length."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = True
        request.content_length = 100
        # Create long JSON string
        long_data = {"description": "A" * 400}
        request.get_json.return_value = long_data

        result = build_request_data(request, "/api/test", max_field_length=50)

        assert result["method"] == "POST"
        assert len(result["json_data"]) == 50

    def test_post_request_parse_exception(self):
        """Test handling of JSON parse exceptions."""
        request = Mock()
        request.method = "POST"
        request.args = None
        request.is_json.return_value = True
        request.content_length = 100
        request.get_json.side_effect = Exception("Invalid JSON")

        result = build_request_data(request, "/api/test")

        assert result["method"] == "POST"
        assert "body_error" in result
        assert "Could not parse request body" in result["body_error"]

    def test_request_without_attributes(self):
        """Test request object missing some attributes."""
        request = Mock()
        request.method = "GET"
        # No args attribute
        del request.args

        result = build_request_data(request, "/api/test")

        assert result["method"] == "GET"
        assert result["query_params"] is None


class TestConstants:
    """Test the constant values."""

    def test_common_bot_endpoints_not_empty(self):
        """Test that common bot endpoints list is not empty."""
        assert len(COMMON_BOT_ENDPOINTS) > 0
        assert "/health*" in COMMON_BOT_ENDPOINTS
        assert "/wp-admin/*" in COMMON_BOT_ENDPOINTS

    def test_common_bot_error_codes_not_empty(self):
        """Test that common bot error codes list is not empty."""
        assert len(COMMON_BOT_ERROR_CODES) > 0
        assert 401 in COMMON_BOT_ERROR_CODES
        assert 405 in COMMON_BOT_ERROR_CODES
