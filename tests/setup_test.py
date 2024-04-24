from unittest.mock import patch, MagicMock

import pytest

import config
from setup import Setup


@patch('setup.argparse.ArgumentParser.parse_args')
@patch('setup.Setup._Setup__check_directory')
def test_setup_initialization(mock_check_directory, mock_parse_args):
    # Setup mock for parse_args
    mock_args = MagicMock()
    mock_args.extractor_name = 'best_frames_extractor'
    mock_args.input = '/fake/input/directory'
    mock_args.output = '/fake/output/directory'
    mock_args.port = 8080
    mock_parse_args.return_value = mock_args

    # Setup mock for directory check, assuming it just returns the directory path if valid
    mock_check_directory.side_effect = lambda x: x

    # Instantiate Setup to test __init__
    setup_instance = Setup()

    # Assertions to ensure all properties are set correctly
    assert setup_instance.extractor_name == 'best_frames_extractor'
    assert setup_instance.input_directory == '/fake/input/directory'
    assert setup_instance.output_directory == '/fake/output/directory'
    assert setup_instance.port == 8080

    # Ensure the directory check was called correctly
    mock_check_directory.assert_any_call('/fake/input/directory')
    mock_check_directory.assert_any_call('/fake/output/directory')
    mock_check_directory.assert_called_with('/fake/output/directory')

    # Optionally, verify the command-line argument parsing
    mock_parse_args.assert_called_once()

# @pytest.fixture
# def args():
#     # Provide different sets of arguments for testing
#     return [
#         {'extractor_name': 'best_frames_extractor', 'input': '/valid/input', 'output': '/valid/output', 'port': 8000},
#         {'extractor_name': 'top_images_extractor', 'input': '/another/input', 'output': '/another/output', 'port': 9000}
#     ]

# @pytest.mark.parametrize("arg_set", args())
# @patch('your_module.argparse.ArgumentParser.parse_args')
# @patch('your_module.Setup._Setup__check_directory')
# def test_setup_various_args(mock_check_directory, mock_parse_args, arg_set):
#     # Prepare the mock setup for each parameter set
#     mock_args = MagicMock()
#     mock_args.extractor_name = arg_set['extractor_name']
#     mock_args.input = arg_set['input']
#     mock_args.output = arg_set['output']
#     mock_args.port = arg_set['port']
#     mock_parse_args.return_value = mock_args
#     mock_check_directory.side_effect = lambda x: x
#
#     # Create the Setup instance
#     setup_instance = Setup()
#
#     # Verify that all attributes are set as per the arg set
#     assert setup_instance.extractor_name == arg_set['extractor_name']
#     assert setup_instance.input_directory == arg_set['input']
#     assert setup_instance.output_directory == arg_set['output']
#     assert setup_instance.port == arg_set['port']
#     mock_check_directory.assert_any_call(arg_set['input'])
#     mock_check_directory.assert_any_call(arg_set['output'])
#
#     # Verify parse_args was called correctly
#     mock_parse_args.assert_called_once()