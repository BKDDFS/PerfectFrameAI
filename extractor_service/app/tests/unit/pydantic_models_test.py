from unittest.mock import patch

import pytest
from app.pydantic_models import RequestData, Message, EvaluatorStatus  # Zaktualizuj ścieżkę importu
import os
from tempfile import TemporaryDirectory


def test_evaluator_status():
    status = EvaluatorStatus(active_evaluator=None)
    assert status.active_evaluator is None

    status = EvaluatorStatus(active_evaluator="BestFramesExtractor")
    assert status.active_evaluator == "BestFramesExtractor"


def test_message():
    msg = Message(message="Test message")
    assert msg.message == "Test message"


def test_request_data_validation_success():
    with TemporaryDirectory() as tempdir:
        input_dir = os.path.join(tempdir, "input")
        output_dir = os.path.join(tempdir, "output")
        os.mkdir(input_dir)
        os.mkdir(output_dir)

        request_data = RequestData(input_folder=input_dir, output_folder=output_dir)
        assert request_data.input_folder == input_dir
        assert request_data.output_folder == output_dir


def test_request_data_validation_failure_output():
    with pytest.raises(NotADirectoryError, match=f"The path 'output_path' is not a directory."):
        RequestData(input_folder="C:\\", output_folder="output_path")


def test_request_data_validation_failure_input():
    with pytest.raises(NotADirectoryError, match=f"The path 'input_path' is not a directory."):
        RequestData(input_folder="input_path", output_folder="C:\\")


def test_validate_output_folder_raises_os_error():
    with patch("os.makedirs") as mock_makedirs:
        mock_makedirs.side_effect = OSError("Simulated OSError")

        with pytest.raises(OSError, match="Failed to create directory") as exc_info:
            RequestData(input_folder="C:\\", output_folder="C:\\")

