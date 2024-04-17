import logging
import re

from unittest.mock import Mock, patch, MagicMock

import cv2
import numpy as np
import pytest
import torch
from freezegun import freeze_time

from app.evaluator import Evaluator

TEST_INPUT_FOLDER = "some/input/folder/path/"
TEST_OUTPUT_FOLDER = "some/output/folder/path/"
TEST_BGR_FRAME = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
TEST_RGB_FRAME = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
TEST_TENSOR_FRAME = torch.Tensor
EXPECTED_RESULT = "some_value"
TEST_AVAILABLE_EXTENSIONS = (".avi", ".mp4", ".mov", ".webm", ".wmv", ".flv")
TEST_VALID_EXTENSION = ".mp4"
TEST_FILE_PATHS = ["path1", "path2"]


class TestEvaluator(Evaluator):
    def process(self, input_folder):
        pass


def test_evaluator_initialization():
    with patch("app.evaluator.Evaluator.get_torch_device") as mock_get_device, \
            patch("app.evaluator.Evaluator._check_folder_exists") as mock_check_folder:
        iqa_metric = MagicMock()
        transforms_compose = MagicMock()
        evaluator = TestEvaluator(TEST_OUTPUT_FOLDER, iqa_metric=iqa_metric, transforms_compose=transforms_compose)
        mock_get_device.assert_called_once()
        mock_check_folder.assert_called_once_with(TEST_OUTPUT_FOLDER)
    assert evaluator is not None
    assert evaluator.device is not None
    assert evaluator.output_folder == TEST_OUTPUT_FOLDER
    assert evaluator.iqa_metric is not None
    assert evaluator.transforms_compose is not None


@pytest.fixture
def evaluator():
    with patch("app.evaluator.Evaluator.get_torch_device"), \
            patch("app.evaluator.Evaluator._check_folder_exists"):
        iqa_metric = Mock()
        transforms_compose = Mock()
        return TestEvaluator(TEST_OUTPUT_FOLDER, iqa_metric=iqa_metric, transforms_compose=transforms_compose)


def test_check_folder_exists(evaluator):
    with patch("app.evaluator.os.path.exists", return_value=False) as mock_os_exists, \
            patch("app.evaluator.os.makedirs") as mock_makedirs:
        evaluator._check_folder_exists(TEST_OUTPUT_FOLDER)
        mock_os_exists.assert_called_once_with(TEST_OUTPUT_FOLDER)
        mock_makedirs.assert_called_once_with(TEST_OUTPUT_FOLDER)


@pytest.mark.parametrize("is_available", (True, False))
def test_get_torch_device(evaluator, is_available, caplog):
    with patch("torch.cuda.is_available", return_value=is_available) as mock_cuda_is_available:
        with caplog.at_level(logging.DEBUG):
            result = evaluator.get_torch_device()
        mock_cuda_is_available.assert_called_once()
    if is_available:
        assert "Using CUDA for processing." in caplog.messages[0]
        assert result.type == 'cuda'
    else:
        assert "CUDA is not available!!! Using CPU for processing." in caplog.messages[0]
        assert result.type == 'cpu'
    assert isinstance(result, torch.device)


def test_score_frame(evaluator, caplog):
    evaluator.convert_frame_bgr_to_rgb = Mock(return_value=TEST_RGB_FRAME)
    evaluator.convert_frame_rgb_to_tensor = Mock(return_value=TEST_TENSOR_FRAME)
    evaluator.iqa_metric = MagicMock(return_value=MagicMock())
    evaluator.iqa_metric.return_value.item = MagicMock(return_value=EXPECTED_RESULT)
    with caplog.at_level(logging.DEBUG):
        result = evaluator._score_frame(TEST_BGR_FRAME)
    evaluator.convert_frame_bgr_to_rgb.assert_called_once_with(TEST_BGR_FRAME)
    evaluator.convert_frame_rgb_to_tensor.assert_called_once_with(TEST_RGB_FRAME,
                                                                  evaluator.transforms_compose, evaluator.device)
    evaluator.iqa_metric.return_value.item.assert_called_once()
    assert f"Frame scored. Score: {result}" in caplog.messages[0]
    assert result == EXPECTED_RESULT


def test_convert_frame_bgr_to_rgb(evaluator, caplog):
    with patch("cv2.cvtColor", return_value=EXPECTED_RESULT) as mock_cv2_cvtColor:
        with caplog.at_level(logging.DEBUG):
            result = evaluator.convert_frame_bgr_to_rgb(TEST_BGR_FRAME)
        mock_cv2_cvtColor.assert_called_once_with(TEST_BGR_FRAME, cv2.COLOR_BGR2RGB)
    assert "Frame converted from BGR to RGB." in caplog.messages[0]
    assert result == EXPECTED_RESULT


def test_convert_frame_rgb_to_tensor(evaluator, caplog):
    evaluator.transforms_compose = MagicMock(return_value=MagicMock())
    evaluator.transforms_compose.return_value.unsqueeze = MagicMock(return_value=MagicMock())
    evaluator.transforms_compose.return_value.unsqueeze.return_value.to = MagicMock(return_value=EXPECTED_RESULT)
    with caplog.at_level(logging.DEBUG):
        result = evaluator.convert_frame_rgb_to_tensor(TEST_RGB_FRAME, evaluator.transforms_compose, evaluator.device)
    evaluator.transforms_compose.assert_called_once_with(TEST_RGB_FRAME)
    evaluator.transforms_compose.return_value.unsqueeze.assert_called_once_with(0)
    evaluator.transforms_compose.return_value.unsqueeze.return_value.to.assert_called_once_with(evaluator.device)
    assert "Frame converted from RGB to TENSOR." in caplog.messages[0]
    assert result == EXPECTED_RESULT


@freeze_time("2023-01-01 00:00:00")
def test_save_ndarray_frame(evaluator, caplog):
    expected_frame_name = f"best_frame_1672531200000.jpg"
    expected_frame_path = f"{TEST_OUTPUT_FOLDER}{expected_frame_name}"
    with patch("cv2.imwrite") as mock_imwrite, \
            caplog.at_level(logging.DEBUG):
        result = evaluator.save_ndarray_frame(TEST_OUTPUT_FOLDER, TEST_BGR_FRAME)
    mock_imwrite.assert_called_once_with(expected_frame_path, TEST_BGR_FRAME)
    assert f"Frame saved at '{expected_frame_path}'." in caplog.messages[0]
    assert result == expected_frame_path


@pytest.mark.parametrize("file_paths", (TEST_FILE_PATHS, None))
def test_get_files_with_specific_extension_from_folder(evaluator, caplog, file_paths):
    expected_logger_massage = (f"Couldn't find any files with "
                               f"extension '{TEST_VALID_EXTENSION}' in folder '{TEST_INPUT_FOLDER}'.")
    expected_glob_pattern = f"{TEST_INPUT_FOLDER}*{TEST_VALID_EXTENSION}"
    evaluator.check_extension_is_valid = Mock()

    with patch("app.evaluator.os.path.isdir",
               return_value=True) as mock_isdir, \
            patch("app.evaluator.glob",
                  return_value=file_paths) as mock_glob, \
            caplog.at_level(logging.DEBUG):
        result = evaluator.get_files_with_specific_extension_from_folder(TEST_INPUT_FOLDER,
                                                                         TEST_VALID_EXTENSION,
                                                                         TEST_AVAILABLE_EXTENSIONS)
        if file_paths:
            assert result == file_paths
            evaluator.check_extension_is_valid.assert_called_once_with(TEST_VALID_EXTENSION, TEST_AVAILABLE_EXTENSIONS)
            assert not caplog.messages
        else:
            assert result is None
            assert expected_logger_massage in caplog.messages[0]
        evaluator.check_extension_is_valid.assert_called_once_with(TEST_VALID_EXTENSION, TEST_AVAILABLE_EXTENSIONS)
        mock_isdir.assert_called_once()
        mock_glob.assert_called_once_with(expected_glob_pattern)


def test_get_files_with_specific_extension_from_folder_invalid_folder(evaluator):
    with pytest.raises(ValueError, match=f"Can't find folder '{TEST_INPUT_FOLDER}'."):
        result = evaluator.get_files_with_specific_extension_from_folder(TEST_INPUT_FOLDER,
                                                                         TEST_VALID_EXTENSION,
                                                                         TEST_AVAILABLE_EXTENSIONS)
        assert not result


def test_check_extension_is_valid_valid_extension(evaluator):
    result = evaluator.check_extension_is_valid(TEST_VALID_EXTENSION, TEST_AVAILABLE_EXTENSIONS)
    assert result is True


def test_check_extension_is_valid_invalid_extension(evaluator):
    invalid_extension = ".jpg"
    expected_error_message = re.escape(f"You provided invalid video extension: {invalid_extension}. "
                                       f"Available extensions: {TEST_AVAILABLE_EXTENSIONS}")
    with pytest.raises(ValueError, match=expected_error_message):
        result = evaluator.check_extension_is_valid(invalid_extension, TEST_AVAILABLE_EXTENSIONS)
        assert not result
