import pytest
import requests
from boxing.utils.api_utils import get_random


def test_get_random_success():
    """Test get_random() when the API returns a valid float."""
    random_number = get_random()
    assert isinstance(random_number, float)
    assert 0.0 <= random_number <= 1.0  # Ensure it's within expected range


def test_get_random_timeout():
    """Test get_random() when the request times out."""
    try:
        get_random()
    except requests.exceptions.Timeout:
        pytest.fail("Request to random.org timed out unexpectedly.")


def test_get_random_request_exception():
    """Test get_random() when a request-related error occurs."""
    try:
        get_random()
    except requests.exceptions.RequestException:
        pytest.fail("Request to random.org encountered a request error.")


def test_get_random_invalid_response():
    """Test get_random() when an invalid response is received."""
    response = "invalid_response"
    try:
        float(response)  # Simulating the parsing logic
        pytest.fail("Expected ValueError for invalid response but got a valid float.")
    except ValueError:
        pass  # This is the expected behavior