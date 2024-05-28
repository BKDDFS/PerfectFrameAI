import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from extractor_service.app.image_evaluators import _ResNetModel


@pytest.fixture(autouse=True)
def reset_resnet_model():
    _ResNetModel.reset()
    yield
    _ResNetModel.reset()


def test_get_prediction_weights():
    result = _ResNetModel.get_prediction_weights()

    assert result is _ResNetModel._prediction_weights


@patch("extractor_service.app.image_evaluators.tf.keras.applications.InceptionResNetV2")
@patch("extractor_service.app.image_evaluators.Dropout")
@patch("extractor_service.app.image_evaluators.Dense")
@patch("extractor_service.app.image_evaluators.Model")
def test_create_model(mock_model, mock_dense, mock_dropout, mock_resnet, caplog):
    model_weights_path = Path("/fake/path/to/weights.h5")
    model_inputs = "mock_input"
    model_outputs = "mock_output"
    processed_output = "mock_processed_output"
    final_output = "mock_final_output"

    mock_base_model_instance = MagicMock()
    mock_resnet.return_value = mock_base_model_instance
    mock_base_model_instance.output = model_outputs
    mock_base_model_instance.input = model_inputs
    mock_dropout_instance = MagicMock()
    mock_dropout.return_value = mock_dropout_instance
    mock_dropout_instance.return_value = processed_output
    mock_dense_instance = MagicMock()
    mock_dense.return_value = mock_dense_instance
    mock_dense_instance.return_value = final_output
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance
    mock_model_instance.load_weights = MagicMock()

    with caplog.at_level(logging.DEBUG):
        model = _ResNetModel._create_model(model_weights_path)

    mock_resnet.assert_called_once_with(input_shape=(224, 224, 3), include_top=False, pooling="avg", weights=None)
    mock_dropout.assert_called_once_with(_ResNetModel._dropout_rate)
    mock_dense.assert_called_once_with(_ResNetModel._num_classes, activation="softmax")
    mock_model.assert_called_once_with(inputs=model_inputs, outputs=final_output)
    mock_model_instance.load_weights.assert_called_once_with(model_weights_path)
    assert "Model loaded successfully." in caplog.text
    assert model == mock_model_instance


def test_class_arguments():
    model = _ResNetModel
    assert model._config is None
    assert model._model is None
    assert list(model._prediction_weights) == list(np.arange(1, 11))
    assert model._input_shape == (224, 224, 3)
    assert model._dropout_rate == 0.75
    assert model._num_classes == 10


def test_reset(config):
    model = "some_model"
    _ResNetModel._model = model
    _ResNetModel._config = config

    _ResNetModel.reset()

    assert _ResNetModel._model is None
    assert _ResNetModel._config is None


@pytest.mark.parametrize("had_model", (True, False))
@patch.object(_ResNetModel, "_get_model_weights")
@patch.object(_ResNetModel, "_create_model")
def test_get_model(mock_create, mock_get_weights, had_model, config):
    weights = "some_weights"
    model = "some_model"
    mock_get_weights.return_value = weights
    mock_create.return_value = model

    assert _ResNetModel._model is None

    if had_model:
        _ResNetModel._model = model

    result = _ResNetModel.get_model(config)

    if had_model:
        mock_get_weights.assert_not_called()
        mock_create.assert_not_called()
        assert _ResNetModel._config != config
        assert result == model
    else:
        mock_get_weights.assert_called_once()
        mock_create.assert_called_once_with(weights)
        assert _ResNetModel._config == config
        assert _ResNetModel._model == result
        assert result == model


@pytest.mark.parametrize("file_exists", (True, False))
@patch.object(Path, "is_file")
@patch.object(_ResNetModel, "_download_model_weights")
def test_get_model_weights(mock_download, mock_is_file, file_exists, caplog):
    mock_is_file.return_value = file_exists
    test_directory = "/fake/directory"
    test_filename = "weights.h5"
    _ResNetModel._config = MagicMock(weights_directory=test_directory, weights_filename=test_filename)
    expected_path = Path(test_directory) / test_filename

    with caplog.at_level(logging.DEBUG):
        result = _ResNetModel._get_model_weights()

    assert f"Searching for model weights in weights directory: {test_directory}" in caplog.text
    if file_exists:
        assert f"Model weights loaded from: {expected_path}" in caplog.text
        mock_download.assert_not_called()
    else:
        assert f"Can't find model weights in weights directory: {test_directory}" in caplog.text
        mock_download.assert_called_once_with(expected_path)
    assert result == expected_path


@pytest.mark.parametrize("status_code", (200, 404))
@patch.object(Path, "write_bytes")
@patch("extractor_service.app.image_evaluators.requests.get")
@patch.object(Path, "mkdir")
def test_download_model_weights_success(mock_mkdir, mock_get, mock_write_bytes, status_code, caplog):
    test_url = "http://example.com/weights.h5"
    test_path = Path("/fake/path/to/weights.h5")
    _ResNetModel._config = MagicMock(weights_repo_url="http://example.com/", weights_filename="weights.h5")
    weights_data = b"weights data"
    timeout = 12

    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = weights_data
    mock_get.return_value = mock_response

    if status_code == 200:
        with caplog.at_level(logging.DEBUG):
            _ResNetModel._download_model_weights(test_path, timeout)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_bytes.assert_called_once_with(weights_data)
        assert f"Model weights downloaded and saved to {test_path}" in caplog.text
    else:
        error_message = f"Failed to download the weights: HTTP status code {status_code}"
        with caplog.at_level(logging.DEBUG), \
                pytest.raises(_ResNetModel.DownloadingModelWeightsError, match=error_message):
            _ResNetModel._download_model_weights(test_path, timeout)
        assert "Failed to download the weights: HTTP status code 404" in caplog.text
    assert f"Downloading model weights from ulr: {test_url}" in caplog.text
    mock_get.assert_called_once_with(test_url, allow_redirects=True, timeout=timeout)
