import logging
from datetime import time
from http.client import RemoteDisconnected
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from setup import Setup, check_directory

EXTRACTOR_NAME = "test_extractor"
INPUT_DIRECTORY = Path("mock/input")
OUTPUT_DIRECTORY = Path("mock/output")
PORT = 8000


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


# @patch('urllib.request.Request')
# @patch('time.time')
# @patch.object(Setup, '_try_to_run_extractor')
# def test_run_extractor(mock_try_to_run_extractor, mock_time, mock_request, setup):
#     mock_try_to_run_extractor.side_effect = [False, False, True]  # will loop three times
#
#     setup.run_extractor()
#
#     assert mock_try_to_run_extractor.call_count == 3, "The loop did not execute the expected number of times"
#     assert mock_request.call_count == 1, "Request was not created"
#     # mock_request.assert_called_with(f"http://localhost:8080/extractors/test_extractor", method="POST")
#
#     assert mock_time.call_count == 1, "Time was not checked correctly"


@patch('setup.urlopen')
@patch('setup.time.time')
@patch('setup.time.sleep')  # Mock sleep to ensure no delay in the test
def test_try_to_run_extractor(mock_sleep, mock_time, mock_urlopen, setup):
    # Setup for time mocking
    start_time = 100
    mock_time.side_effect = [start_time, start_time + 30, start_time + 65]  # Normal progression, then timeout

    # Setup for urlopen mock
    response_mock = MagicMock()
    response_mock.status = 200
    response_mock.read.return_value = 'Successful response'
    mock_urlopen.return_value = response_mock

    # Test successful request
    req = MagicMock()
    assert setup._try_to_run_extractor(req, start_time) is True
    response_mock.read.assert_called_once()
    mock_sleep.assert_not_called()

    # Test the function with a disconnection
    mock_urlopen.side_effect = RemoteDisconnected("Remote host closed connection")
    assert setup._try_to_run_extractor(req, start_time) is False
    mock_sleep.assert_called_once_with(3)

    # Test timeout
    mock_urlopen.side_effect = lambda x: time.sleep(1)  # Delay to trigger timeout
    with pytest.raises(TimeoutError) as exc_info:
        setup._try_to_run_extractor(req, start_time)
    assert "Timed out waiting for service to respond." in str(exc_info.value)
    assert mock_time.call_count >= 3  # Ensure time was checked multiple times