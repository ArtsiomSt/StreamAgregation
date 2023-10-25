from unittest.mock import MagicMock
import requests

print("START OF THE TESTS")


def mock_request_get(*args, **kwargs):
    print('mocked_get_request')
    return {"detail": "mocked_response"}


requests.get = MagicMock(side_effect=mock_request_get)
