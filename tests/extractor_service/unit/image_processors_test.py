import logging
import uuid
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import cv2
import numpy as np

from extractor_service.app.image_processors import OpenCVImage


@patch.object(cv2, "imread")
def test_read_image(mock_imread, caplog):
    mock_path = Path("some/path/to/image.jpg")
    expected_image = MagicMock(spec=np.ndarray)
    mock_imread.return_value = expected_image

    with caplog.at_level(logging.DEBUG):
        result = OpenCVImage.read_image(mock_path)

    assert result == expected_image
    mock_imread.assert_called_once_with(str(mock_path))
    assert f"Image '{mock_path}' has successfully read." in caplog.text


@patch.object(cv2, "imread")
def test_read_image_invalid_image(mock_imread, caplog):
    mock_path = Path("some/path/to/image.jpg")
    mock_imread.return_value = None

    with caplog.at_level(logging.WARNING):
        result = OpenCVImage.read_image(mock_path)

    assert result is None
    mock_imread.assert_called_once_with(str(mock_path))
    assert (f"Can't read image. OpenCV reading not returns np.ndarray"
            f" for image path: {str(mock_path)}") in caplog.text


@patch.object(uuid, "uuid4")
@patch.object(cv2, "imwrite")
def test_save_image(mock_imwrite, mock_uuid, caplog):
    file_name = "some_filename"
    mock_uuid.return_value = file_name
    fake_image = MagicMock(spec=np.ndarray)
    output_directory = Path("/fake/directory")
    output_format = ".jpg"
    expected_path = output_directory / f"image_{file_name}{output_format}"

    with caplog.at_level(logging.DEBUG):
        image_path = OpenCVImage.save_image(fake_image, output_directory, output_format)

    mock_imwrite.assert_called_once_with(str(expected_path), fake_image)
    assert image_path == expected_path, "The returned path does not match the expected path."
    assert f"Image saved at '{expected_path}'." in caplog.text


@patch.object(cv2, "resize")
@patch.object(cv2, "cvtColor")
@patch.object(np, "array")
def test_normalize_images(mock_array, mock_cvt, mock_resize, caplog):
    images_num = 3
    target_size = (112, 112)
    batch_images = [MagicMock(spec=np.ndarray) for _ in range(images_num)]
    resized_images = [MagicMock(spec=np.ndarray) for _ in range(images_num)]
    expected_images = [MagicMock(spec=np.ndarray) for _ in range(images_num)]
    mock_resize.side_effect = resized_images
    mock_cvt.side_effect = expected_images
    mock_array.return_value = np.array(expected_images, dtype=np.float32) / 255.0

    result = OpenCVImage.normalize_images(batch_images, target_size)

    calls = [call(
        image,
        target_size,
        interpolation=cv2.INTER_LANCZOS4
    ) for image in batch_images]
    mock_resize.assert_has_calls(calls, any_order=True)
    calls = [call(
        image,
        cv2.COLOR_BGR2RGB
    ) for image in resized_images]
    mock_cvt.assert_has_calls(calls, any_order=True)
    np.testing.assert_array_equal(result, mock_array.return_value)
