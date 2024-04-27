import logging
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest

from extractor_service.app.image_processors import OpenCVImage


@pytest.fixture
def opencv():
    opencv = OpenCVImage()
    return opencv


@patch.object(cv2, "imread")
def test_read_image(mock_imread, opencv, caplog):
    mock_path = Path("some/path/to/image.jpg")
    expected_image = MagicMock(spec=np.ndarray)
    mock_imread.return_value = expected_image

    with caplog.at_level(logging.DEBUG):
        result = opencv.read_image(mock_path)

    assert result == expected_image
    mock_imread.assert_called_once_with(str(mock_path))
    assert f"Image '{mock_path}' has successfully read." in caplog.text


@patch.object(cv2, "imread")
def test_read_image_invalid_image(mock_imread, opencv, caplog):
    mock_path = Path("some/path/to/image.jpg")
    mock_imread.return_value = None

    with caplog.at_level(logging.WARNING):
        result = opencv.read_image(mock_path)

    assert result is None
    mock_imread.assert_called_once_with(str(mock_path))
    assert (f"Can't read image. OpenCV reading not returns np.ndarray"
            f" for image path: {str(mock_path)}") in caplog.text


@patch.object(uuid, "uuid4")
@patch.object(cv2, "imwrite")
def test_save_image(mock_imwrite, mock_uuid, opencv, caplog):
    file_name = "some_filename"
    mock_uuid.return_value = file_name
    fake_image = MagicMock(spec=np.ndarray)
    output_directory = Path("/fake/directory")
    output_format = ".jpg"
    expected_path = output_directory / f"image_{file_name}{output_format}"

    with caplog.at_level(logging.DEBUG):
        image_path = opencv.save_image(fake_image, output_directory, output_format)

    mock_imwrite.assert_called_once_with(str(expected_path), fake_image)
    assert image_path == expected_path, "The returned path does not match the expected path."
    assert f"Image saved at '{expected_path}'." in caplog.text
