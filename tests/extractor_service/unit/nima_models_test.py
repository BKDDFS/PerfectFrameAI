import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from extractor_service.app.image_evaluators import _ONNXModel


def test_get_prediction_weights():
    result = _ONNXModel.get_prediction_weights()

    assert list(result) == list(np.arange(1, 11))


def test_class_arguments():
    model = _ONNXModel
    assert list(model._prediction_weights) == list(np.arange(1, 11))


@pytest.mark.parametrize("file_exists", (True, False))
@patch.object(Path, "is_file")
@patch.object(_ONNXModel, "_download_model_weights")
def test_get_model_path(mock_download, mock_is_file, file_exists, config, caplog):
    mock_is_file.return_value = file_exists
    expected_path = Path(config.weights_directory) / config.weights_filename

    with caplog.at_level(logging.DEBUG):
        result = _ONNXModel.get_model_path(config)

    assert f"Searching for model weights in weights directory: {config.weights_directory}" in caplog.text
    if file_exists:
        assert f"Model weights loaded from: {expected_path}" in caplog.text
        mock_download.assert_not_called()
    else:
        assert f"Can't find model weights in weights directory: {config.weights_directory}" in caplog.text
        mock_download.assert_called_once_with(expected_path, config)
    assert result == expected_path


@pytest.mark.parametrize("status_code", (200, 404))
@patch.object(Path, "write_bytes")
@patch("extractor_service.app.image_evaluators.requests.get")
@patch.object(Path, "mkdir")
def test_download_model_weights(mock_mkdir, mock_get, mock_write_bytes, status_code, config, caplog):
    test_path = Path("/fake/path/to/weights.onnx")
    test_url = f"{config.weights_repo_url}{config.weights_filename}"
    weights_data = b"weights data"
    timeout = 12

    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = weights_data
    mock_get.return_value = mock_response

    if status_code == 200:
        with caplog.at_level(logging.DEBUG):
            _ONNXModel._download_model_weights(test_path, config, timeout)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_bytes.assert_called_once_with(weights_data)
        assert f"Model weights downloaded and saved to {test_path}" in caplog.text
    else:
        error_message = f"Failed to download the weights: HTTP status code {status_code}"
        with (
            caplog.at_level(logging.DEBUG),
            pytest.raises(_ONNXModel.DownloadingModelWeightsError, match=error_message),
        ):
            _ONNXModel._download_model_weights(test_path, config, timeout)
        assert "Failed to download the weights: HTTP status code 404" in caplog.text
    assert f"Downloading model weights from ulr: {test_url}" in caplog.text
    mock_get.assert_called_once_with(test_url, allow_redirects=True, timeout=timeout)