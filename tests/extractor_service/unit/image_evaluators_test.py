import logging
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest

from extractor_service.app.image_evaluators import (InceptionResNetNIMA,
                                                    _ResNetModel)


@pytest.fixture
def evaluator():
    with patch.object(_ResNetModel, "get_model", return_value=MagicMock()):
        evaluator = InceptionResNetNIMA(MagicMock())
    return evaluator


@patch.object(_ResNetModel, "get_model")
def test_evaluator_initialization(mock_get_model, config):
    test_model = "some_model"
    mock_get_model.return_value = test_model

    instance = InceptionResNetNIMA(config)

    mock_get_model.assert_called_once()
    assert instance._model == test_model


@patch("extractor_service.app.image_evaluators.convert_to_tensor")
@patch.object(InceptionResNetNIMA, "_calculate_weighted_mean")
@patch.object(InceptionResNetNIMA, "_check_scores")
def test_evaluate_images(mock_check, mock_calculate, mock_convert_to_tensor, evaluator, caplog):
    fake_images = MagicMock(spec=np.ndarray)
    fake_images.shape = (3, 2, 2)
    tensor = "some_tensor"
    predictions = [1.0, 2.0, 3.0]
    expected_scores = [10.0, 20.0, 30.0]
    mock_convert_to_tensor.return_value = tensor
    mock_calculate.side_effect = expected_scores
    evaluator._model.predict.return_value = predictions

    with caplog.at_level(logging.INFO):
        result = evaluator.evaluate_images(fake_images)

    mock_convert_to_tensor.assert_called_once_with(fake_images)
    evaluator._model.predict.assert_called_once_with(tensor, batch_size=fake_images.shape[0], verbose=0)
    mock_calculate.assert_has_calls([
        call(prediction, _ResNetModel._prediction_weights) for prediction in predictions],
        any_order=True
    )
    mock_check.assert_called_once()
    assert "Evaluating images..." in caplog.text
    assert "Images batch evaluated." in caplog.text
    assert result == expected_scores


def test_calculate_weighted_mean_with_default_weights(evaluator):
    prediction = np.array([10, 20, 30])
    expected_weighted_mean = np.mean(prediction)  # Since default weights are equal

    calculated_mean = evaluator._calculate_weighted_mean(prediction)

    assert np.isclose(calculated_mean, expected_weighted_mean)


def test_calculate_weighted_mean_with_custom_weights(evaluator):
    prediction = np.array([10, 20, 30])
    weights = np.array([1, 2, 3])
    expected_weighted_mean = np.sum(prediction * weights) / np.sum(weights)

    calculated_mean = evaluator._calculate_weighted_mean(prediction, weights)

    assert np.isclose(calculated_mean, expected_weighted_mean)


@pytest.mark.parametrize("score_len, images_len", ((1, 1), (1, 2)))
def test_check_scores(score_len, images_len, evaluator, caplog):
    scores = [MagicMock(spec=np.ndarray) for _ in range(score_len)]
    images = [MagicMock(spec=float) for _ in range(images_len)]
    with caplog.at_level(logging.DEBUG):
        evaluator._check_scores(images, scores)

    assert f"Scores: {scores}" in caplog.text
    if score_len == images_len:
        assert f"Scores and images lists length: {score_len}" in caplog.text
    else:
        assert "Scores and images lists lengths don't match!" in caplog.text
        assert f"Images list length: {images_len}" in caplog.text
        assert f"Scores list length: {score_len}" in caplog.text
