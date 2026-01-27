import logging

import numpy as np
import pytest

from perfectframe.image_evaluators import InceptionResNetNIMA, _ONNXModel


@pytest.fixture
def evaluator(mocker):
    mocker.patch.object(_ONNXModel, "get_model_path", return_value="/fake/path/model.onnx")
    mock_session = mocker.patch("perfectframe.image_evaluators.ort.InferenceSession")
    mock_session_instance = mocker.MagicMock()
    mock_session_instance.get_inputs.return_value = [mocker.MagicMock(name="input")]
    mock_session.return_value = mock_session_instance
    return InceptionResNetNIMA(mocker.MagicMock())


def test_evaluator_initialization(mocker, config):
    mock_get_path = mocker.patch.object(_ONNXModel, "get_model_path")
    mock_session = mocker.patch("perfectframe.image_evaluators.ort.InferenceSession")
    test_path = "/some/path/model.onnx"
    mock_get_path.return_value = test_path
    mock_session_instance = mocker.MagicMock()
    mock_input = mocker.MagicMock()
    mock_input.name = "input"
    mock_session_instance.get_inputs.return_value = [mock_input]
    mock_session.return_value = mock_session_instance

    instance = InceptionResNetNIMA(config)

    mock_get_path.assert_called_once_with(config)
    mock_session.assert_called_once_with(test_path)
    assert instance._session == mock_session_instance
    assert instance._input_name == "input"


def test_evaluate_images(mocker, evaluator, caplog):
    mock_calculate = mocker.patch.object(InceptionResNetNIMA, "_calculate_weighted_mean")
    mock_check = mocker.patch.object(InceptionResNetNIMA, "_check_scores")
    fake_images = mocker.MagicMock(spec=np.ndarray)
    fake_images.shape = (3, 2, 2)
    fake_images.astype.return_value = fake_images
    predictions = np.array([[0.1] * 10, [0.2] * 10, [0.3] * 10])
    expected_scores = [10.0, 20.0, 30.0]
    mock_calculate.side_effect = expected_scores
    evaluator._session.run.return_value = [predictions]

    with caplog.at_level(logging.INFO):
        result = evaluator.evaluate_images(fake_images)

    predictions_count = 3
    fake_images.astype.assert_called_once_with(np.float32)
    evaluator._session.run.assert_called_once_with(None, {evaluator._input_name: fake_images})
    assert mock_calculate.call_count == predictions_count
    for i, call_args in enumerate(mock_calculate.call_args_list):
        np.testing.assert_array_equal(call_args[0][0], predictions[i])
        np.testing.assert_array_equal(call_args[0][1], _ONNXModel._prediction_weights)
    mock_check.assert_called_once()
    assert "Evaluating images..." in caplog.text
    assert "Images batch evaluated." in caplog.text
    assert result == expected_scores


def test_evaluate_images_returns_empty_list_when_predictions_not_ndarray(mocker, evaluator):
    fake_images = mocker.MagicMock(spec=np.ndarray)
    fake_images.astype.return_value = fake_images
    evaluator._session.run.return_value = [None]

    result = evaluator.evaluate_images(fake_images)

    assert result == []


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


@pytest.mark.parametrize(("score_len", "images_len"), [(1, 1), (1, 2)])
def test_check_scores(mocker, score_len, images_len, evaluator, caplog):
    scores = [mocker.MagicMock(spec=np.ndarray) for _ in range(score_len)]
    images = [mocker.MagicMock(spec=float) for _ in range(images_len)]
    with caplog.at_level(logging.DEBUG):
        evaluator._check_scores(images, scores)

    assert f"Scores: {scores}" in caplog.text
    if score_len == images_len:
        assert f"Scores and images lists length: {score_len}" in caplog.text
    else:
        assert "Scores and images lists lengths don't match!" in caplog.text
        assert f"Images list length: {images_len}" in caplog.text
        assert f"Scores list length: {score_len}" in caplog.text
