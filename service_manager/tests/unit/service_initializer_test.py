import argparse
import json
import logging
import time
import urllib.request
from http.client import RemoteDisconnected
from pathlib import Path
from unittest import mock
from unittest.mock import patch, MagicMock

import pytest

from service_manager import service_initializer
from service_manager.service_initializer import ServiceInitializer


@pytest.fixture
def service(config):
    user_input = MagicMock(
        spec=argparse.Namespace,
        extractor_name=config.service_name,
        input_dir=config.input_directory,
        output_dir=config.output_directory,
        port=config.port
    )
    with patch.object(ServiceInitializer, "_check_directory"):
        initializer = ServiceInitializer(user_input)
    return initializer


@pytest.mark.parametrize("arg_set", (
        {"extractor_name": "best_frames_extractor",
         "input": "/valid/input", "output": "/valid/output", "port": 8000},
        {"extractor_name": "top_images_extractor",
         "input": "/another/input", "output": "/another/output", "port": 9000}
))
@patch.object(ServiceInitializer, "_check_directory")
def test_start_various_args(mock_check_directory, arg_set):
    user_input = MagicMock(
        spec=argparse.Namespace,
        extractor_name=arg_set["extractor_name"],
        input_dir=arg_set["input"],
        output_dir=arg_set["output"],
        port=arg_set["port"]
    )
    mock_check_directory.side_effect = lambda x: x

    service = ServiceInitializer(user_input)

    assert service.extractor_name == arg_set["extractor_name"]
    assert service.input_directory == arg_set["input"]
    assert service.output_directory == arg_set["output"]
    assert service.port == arg_set["port"]
    mock_check_directory.assert_any_call(arg_set["input"])
    mock_check_directory.assert_any_call(arg_set["output"])


def test_check_invalid_directory(caplog):
    invalid_directory = Path("/invalid/input")
    error_massage = f"Invalid directory path: {str(invalid_directory)}"

    with pytest.raises(NotADirectoryError), \
            caplog.at_level(logging.ERROR):
        ServiceInitializer._check_directory(str(invalid_directory))

    assert error_massage in caplog.text, "Invalid logging."


def test_check_valid_directory():
    valid_directory = "/valid/input"

    with patch("pathlib.Path.is_dir"):
        result = ServiceInitializer._check_directory(valid_directory)

    assert result
    assert isinstance(result, Path)


@patch.object(time, "time")
def test_run_extractor(mock_time, service):
    test_url = f"http://localhost:{service.port}/extractors/{service.extractor_name}"
    test_method = "POST"
    start_time = 100
    mock_time.side_effect = [start_time, start_time + 1, start_time + 2, start_time + 3]
    mock_try = MagicMock(side_effect=[False, False, True])
    service._try_to_run_extractor = mock_try

    service.run_extractor()

    assert mock_try.call_count == 3
    mock_try.assert_any_call(mock.ANY, start_time)
    last_call = mock_try.call_args
    request_obj = last_call[0][0]
    assert request_obj.method == test_method
    assert request_obj.full_url == test_url


@pytest.fixture
def mock_urlopen():
    with patch.object(service_initializer, "urlopen") as mock_urlopen:
        yield mock_urlopen


@pytest.fixture(scope="module")
def mock_request():
    return MagicMock(spec=urllib.request.Request)


def test_try_to_run_extractor_success(mock_urlopen, service, caplog, mock_request):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_message = "Success"
    response_content = json.dumps({"message": mock_message}).encode('utf-8')
    mock_response.read.return_value = response_content
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with caplog.at_level(logging.INFO):
        result = service._try_to_run_extractor(mock_request, time.time())

    mock_urlopen.assert_called_once_with(mock_request)
    assert result is True
    mock_response.read.assert_called_once()
    assert f"Response from server: {mock_message}" in caplog.text


@patch.object(time, "sleep")
def test_try_to_run_extractor_remote_disconnected(mock_sleep, mock_urlopen, service, caplog, mock_request):
    mock_urlopen.side_effect = RemoteDisconnected
    with caplog.at_level(logging.INFO):
        result = service._try_to_run_extractor(mock_request, time.time())

    mock_sleep.assert_called_with(3)
    mock_urlopen.assert_called_once()
    assert result is False
    assert "Waiting for service to be available..." in caplog.text


@patch.object(time, "time", return_value=3)
def test_try_to_run_extractor_timeout(mock_time, mock_urlopen, service, caplog, mock_request):
    mock_urlopen.side_effect = RemoteDisconnected
    error_massage = "Timed out waiting for service to respond."
    start_time = 1
    with caplog.at_level(logging.ERROR), \
            pytest.raises(TimeoutError, match=error_massage):
        service._try_to_run_extractor(mock_request, start_time, 1)

    mock_urlopen.assert_called_once()
    mock_time.assert_any_call()
    assert error_massage in caplog.text
