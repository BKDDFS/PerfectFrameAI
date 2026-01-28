import logging
import uuid
from pathlib import Path
from unittest.mock import call  # noqa: TID251

import cv2
import numpy as np

from perfectframe.image_processors import OpenCVImage
from perfectframe.schemas import ImageExtension, ImageResolution


def test_read_image(mocker, caplog):
    mock_imread = mocker.patch.object(cv2, "imread")
    mock_path = Path("some/path/to/image.jpg")
    expected_image = mocker.MagicMock(spec=np.ndarray)
    mock_imread.return_value = expected_image

    with caplog.at_level(logging.DEBUG):
        result = OpenCVImage.read_image(mock_path)

    assert result == expected_image
    mock_imread.assert_called_once_with(str(mock_path))
    assert f"Image '{mock_path}' has successfully read." in caplog.text


def test_read_image_invalid_image(mocker, caplog):
    mock_imread = mocker.patch.object(cv2, "imread")
    mock_path = Path("some/path/to/image.jpg")
    mock_imread.return_value = None

    with caplog.at_level(logging.WARNING):
        result = OpenCVImage.read_image(mock_path)

    assert result is None
    mock_imread.assert_called_once_with(str(mock_path))
    assert (
        f"Can't read image. OpenCV reading not returns np.ndarray for image path: {mock_path!s}"
    ) in caplog.text


def test_save_image(mocker, caplog):
    mock_imwrite = mocker.patch.object(cv2, "imwrite")
    mock_uuid = mocker.patch.object(uuid, "uuid4")
    file_name = "some_filename"
    mock_uuid.return_value = file_name
    fake_image = mocker.MagicMock(spec=np.ndarray)
    output_directory = Path("/fake/directory")
    output_format = ImageExtension.JPG
    expected_path = output_directory / f"image_{file_name}{output_format.value}"

    with caplog.at_level(logging.DEBUG):
        image_path = OpenCVImage.save_image(fake_image, output_directory, output_format)

    mock_imwrite.assert_called_once_with(str(expected_path), fake_image)
    assert image_path == expected_path, "The returned path does not match the expected path."
    assert f"Image saved at '{expected_path}'." in caplog.text


def test_normalize_images(mocker):
    mock_resize = mocker.patch.object(cv2, "resize")
    mock_cvt = mocker.patch.object(cv2, "cvtColor")
    mock_array = mocker.patch.object(np, "array")
    images_num = 3
    target_size = ImageResolution(112, 112)
    batch_images = [mocker.MagicMock(spec=np.ndarray) for _ in range(images_num)]
    resized_images = [mocker.MagicMock(spec=np.ndarray) for _ in range(images_num)]
    expected_images = [mocker.MagicMock(spec=np.ndarray) for _ in range(images_num)]
    mock_resize.side_effect = resized_images
    mock_cvt.side_effect = expected_images
    mock_array.return_value = np.array(expected_images, dtype=np.float32) / 255.0

    result = OpenCVImage.normalize_images(batch_images, target_size)

    calls = [call(image, target_size, interpolation=cv2.INTER_LANCZOS4) for image in batch_images]
    mock_resize.assert_has_calls(calls, any_order=True)
    calls = [call(image, cv2.COLOR_BGR2RGB) for image in resized_images]
    mock_cvt.assert_has_calls(calls, any_order=True)
    np.testing.assert_array_equal(result, mock_array.return_value)
