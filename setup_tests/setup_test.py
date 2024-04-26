import logging
import time
import urllib.request
from http.client import RemoteDisconnected
from pathlib import Path
from unittest import mock
from unittest.mock import patch, MagicMock

import pytest

from setup import Setup, check_directory

EXTRACTOR_NAME = "test_extractor"
INPUT_DIRECTORY = Path("mock/input")
OUTPUT_DIRECTORY = Path("mock/output")
PORT = 8000
MOCK_REQUEST = MagicMock(spec=urllib.request.Request)


@pytest.fixture
def setup():
    mock_args = MagicMock()
    mock_args.extractor_name = EXTRACTOR_NAME
    mock_args.input = INPUT_DIRECTORY
    mock_args.output = OUTPUT_DIRECTORY
    mock_args.port = PORT
    with patch("setup.check_directory"), \
            patch("setup.argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_parse_args.return_value = mock_args
        setup = Setup()
    return setup


def test_check_invalid_directory(caplog):
    invalid_directory = Path("/invalid/input")
    error_massage = f"Invalid directory path: {str(invalid_directory)}"

    with pytest.raises(NotADirectoryError), \
            caplog.at_level(logging.ERROR):
        check_directory(str(invalid_directory))

    assert error_massage in caplog.text, "Invalid logging."


def test_check_valid_directory():
    valid_directory = "/valid/input"

    with patch("pathlib.Path.is_dir"):
        result = check_directory(valid_directory)

    assert result
    assert isinstance(result, Path)


@pytest.mark.parametrize("arg_set", (
        {'extractor_name': 'best_frames_extractor',
         'input': '/valid/input', 'output': '/valid/output', 'port': 8000},
        {'extractor_name': 'top_images_extractor',
         'input': '/another/input', 'output': '/another/output', 'port': 9000}
))
@patch('setup.argparse.ArgumentParser.parse_args')
@patch('setup.check_directory')
def test_setup_various_args(mock_check_directory, mock_parse_args, arg_set):
    mock_args = MagicMock()
    mock_args.extractor_name = arg_set['extractor_name']
    mock_args.input = arg_set['input']
    mock_args.output = arg_set['output']
    mock_args.port = arg_set['port']
    mock_parse_args.return_value = mock_args
    mock_check_directory.side_effect = lambda x: x

    setup_instance = Setup()

    assert setup_instance.extractor_name == arg_set['extractor_name']
    assert setup_instance.input_directory == arg_set['input']
    assert setup_instance.output_directory == arg_set['output']
    assert setup_instance.port == arg_set['port']
    mock_check_directory.assert_any_call(arg_set['input'])
    mock_check_directory.assert_any_call(arg_set['output'])

    mock_parse_args.assert_called_once()


@patch("setup.time.time")
def test_run_extractor(mock_time, setup):
    test_url = f"http://localhost:{setup.port}/extractors/{setup.extractor_name}"
    test_method = "POST"
    start_time = 100
    mock_time.side_effect = [start_time, start_time + 1, start_time + 2, start_time + 3]
    mock_try = MagicMock(side_effect=[False, False, True])
    setup._try_to_run_extractor = mock_try

    setup.run_extractor()

    assert mock_try.call_count == 3
    mock_try.assert_any_call(mock.ANY, start_time)
    last_call = mock_try.call_args
    request_obj = last_call[0][0]
    assert request_obj.method == test_method
    assert request_obj.full_url == test_url


@patch("setup.urlopen")
def test_try_to_run_extractor_success(mock_urlopen, setup):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b'Response content'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = setup._try_to_run_extractor(MOCK_REQUEST, time.time())

    mock_urlopen.assert_called_once()
    assert result is True


@patch("setup.urlopen", side_effect=RemoteDisconnected)
@patch("setup.time.sleep")
def test_try_to_run_extractor_remote_disconnected(mock_sleep, mock_urlopen, setup, caplog):
    with caplog.at_level(logging.INFO):
        result = setup._try_to_run_extractor(MOCK_REQUEST, time.time())

    mock_sleep.assert_called_with(3)
    mock_urlopen.assert_called_once()
    assert result is False
    assert "Waiting for service to be available..." in caplog.text


@patch("setup.time.time", return_value=3)
@patch("setup.urlopen", side_effect=RemoteDisconnected)
def test_try_to_run_extractor_timeout(mock_urlopen, mock_time, setup, caplog):
    error_massage = "Timed out waiting for service to respond."
    start_time = 1
    with caplog.at_level(logging.ERROR), \
            pytest.raises(TimeoutError, match=error_massage):
        setup._try_to_run_extractor(MOCK_REQUEST, start_time, 1)

    mock_urlopen.assert_called_once()
    mock_time.assert_any_call()
    assert error_massage in caplog.text
