import logging
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import torch

from extractor_service.app.image_raters import PyIQA


@pytest.fixture
def pyiqa_rater():
    pyiqa_rater = PyIQA()
    return pyiqa_rater


@patch('extractor_service.app.image_raters.transforms.Compose')
@patch('extractor_service.app.image_raters.pyiqa.create_metric')
@patch('extractor_service.app.image_raters.PyIQA._get_torch_device')
@patch('extractor_service.app.image_raters.transforms.ToTensor', return_value=MagicMock(name='ToTensor'))
def test_pyiqa_initialization(mock_to_tensor, mock_get_torch_device, mock_create_metric, mock_transforms_compose):
    mock_model = "some_model"
    mock_device = "cuda"

    # Mock return the device
    mock_get_torch_device.return_value = mock_device

    # Mock metric creation
    metric_instance_mock = MagicMock()
    mock_create_metric.return_value = metric_instance_mock
    metric_instance_mock.to.return_value = metric_instance_mock  # Return itself to simulate chaining

    # Mock transforms.Compose
    transforms_compose_mock = MagicMock()
    mock_transforms_compose.return_value = transforms_compose_mock

    # Call
    pyiqa_instance = PyIQA(mock_model)

    # Verifications
    mock_get_torch_device.assert_called_once()
    mock_create_metric.assert_called_once_with(mock_model, device=mock_device)
    metric_instance_mock.to.assert_called_once_with(mock_device)
    mock_transforms_compose.assert_called_once_with([mock_to_tensor()])  # Check transforms setup

    # Assert instance attributes
    assert pyiqa_instance.torch_device == mock_device, "Torch device not set correctly"
    assert pyiqa_instance.iqa_metric == metric_instance_mock, "Metric model not set correctly"
    assert pyiqa_instance.transforms_compose == transforms_compose_mock, "Transform compose not set correctly"


@patch.object(PyIQA, '_convert_images_to_tensor_batch')
def test_rate_images(mock_convert_images_to_tensor_batch, pyiqa_rater, caplog):
    mock_iqa_metric = MagicMock()
    pyiqa_rater.iqa_metric = mock_iqa_metric
    fake_images = [MagicMock(np.ndarray) for _ in range(5)]
    fake_tensor_batch = MagicMock()
    mock_convert_images_to_tensor_batch.return_value = fake_tensor_batch
    mock_ratings = [3.5, 4.2, 2.8, 4.0, 3.7]
    mock_iqa_metric.return_value.tolist.return_value = mock_ratings

    with caplog.at_level(logging.INFO):
        ratings = pyiqa_rater.rate_images(fake_images)

    mock_convert_images_to_tensor_batch.assert_called_once_with(fake_images)
    mock_iqa_metric.assert_called_once_with(fake_tensor_batch)
    assert ratings == mock_ratings, "The ratings returned do not match the expected ratings."
    assert "Rating images..." in caplog.text
    assert "Images batch rated." in caplog.text


@patch("torch.cuda.is_available",)
@pytest.mark.parametrize("is_available", (True, False))
def test_get_torch_device(mock_is_available, is_available, pyiqa_rater, caplog):
    mock_is_available.return_value = is_available
    with caplog.at_level(logging.INFO):
        result = pyiqa_rater._get_torch_device()

    mock_is_available.assert_called_once()
    if is_available:
        assert "Using CUDA for processing." in caplog.text
        assert result.type == 'cuda'
    else:
        assert "CUDA is unavailable!!! Using CPU for processing." in caplog.text
        assert result.type == 'cpu'
    assert isinstance(result, torch.device)


@patch('torch.Tensor.to')
@patch('torch.stack')
def test_convert_images_to_tensor_batch(mock_stack, mock_to, pyiqa_rater):
    mock_transforms_compose = MagicMock()
    pyiqa_rater.transforms_compose = mock_transforms_compose
    # Setup fake data
    fake_images = [MagicMock(np.ndarray) for _ in range(3)]
    transformed_images = [MagicMock() for _ in range(3)]

    # Use a dictionary to map fake images to transformed images
    image_map = {id(img): trans_img for img, trans_img in zip(fake_images, transformed_images)}
    mock_transforms_compose.side_effect = lambda x: image_map[id(x)]

    tensor_batch = MagicMock()
    mock_stack.return_value = tensor_batch
    mock_to.return_value = tensor_batch  # Simulate sending to device

    # Call the method under test
    result_tensor = pyiqa_rater._convert_images_to_tensor_batch(fake_images)

    # Verify transforms and tensor operations
    assert mock_transforms_compose.call_count == len(fake_images), "Transforms not applied correctly to all images."
    mock_stack.assert_called_once_with(transformed_images)
    mock_to.assert_called_once_with(pyiqa_rater.torch_device)

    # Assert returned tensor is correct
    assert result_tensor is tensor_batch, "Returned tensor batch is not correct."


@patch('torch.stack')
@patch.object(torch.Tensor, "to", return_value=MagicMock())
def test_convert_images_to_tensor_batch(mock_to, mock_stack, pyiqa_rater, caplog):
    mock_transform = MagicMock()
    pyiqa_rater.transforms_compose = mock_transform
    images = [MagicMock(spec=np.ndarray) for _ in range(4)]
    expected_result = MagicMock(spec=torch.Tensor)
    mock_stack.return_value = expected_result
    mock_transform.return_value.to = mock_to
    with caplog.at_level(logging.DEBUG):
        result = pyiqa_rater._convert_images_to_tensor_batch(images)

    assert mock_transform.call_count == len(images)
    assert all(call.args[0] in images for call in mock_transform.call_args_list)
    assert mock_to.call_count == len(images)
    mock_to.assert_called_with(pyiqa_rater.torch_device)
    assert isinstance(result, torch.Tensor), "Result should be a torch.Tensor"
    assert "Images batch converted from RGB to TENSOR." in caplog.text
