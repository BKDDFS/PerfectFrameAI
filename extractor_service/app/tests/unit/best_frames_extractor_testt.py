import logging
import os.path
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock, create_autospec

import cv2
import numpy as np
import pytest

from app.best_frames_extractor import BestFramesExtractor

from extractor_service.app.schemas import ExtractorConfig



TEST_INPUT_FOLDER = "some/input/folder/path/"
TEST_OUTPUT_FOLDER = "some/output/folder/path/"
TEST_BGR_FRAME = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
EXPECTED_RESULT = "some_value"
TEST_VIDEO_FILENAME = "video.mp4"
TEST_VIDEO_PATH = f"{TEST_INPUT_FOLDER}{TEST_VIDEO_FILENAME}"
TEST_VIDEO_EXTENSION = ".mp4"
TEST_DONE_VIDEO_PREFIX = "done_"
TEST_NUMBER_OF_FRAMES = 2
TEST_CAP = MagicMock()


@pytest.fixture(name="evaluator")
def best_frames_extractor_class_fixture() -> BestFramesExtractor:
    with patch("app.evaluator.Evaluator.get_torch_device"), \
            patch("app.evaluator.Evaluator._check_folder_exists"):
        iqa_metric = MagicMock()
        transforms_compose = MagicMock()
        return BestFramesExtractor(TEST_OUTPUT_FOLDER,
                                   iqa_metric=iqa_metric,
                                   transforms_compose=transforms_compose)


def test_process(evaluator, caplog):
    evaluator.extract_best_frames_from_all_videos_in_folder = Mock()
    with caplog.at_level(logging.INFO):
        evaluator.process(TEST_INPUT_FOLDER)
    evaluator.extract_best_frames_from_all_videos_in_folder.assert_called_once_with(TEST_INPUT_FOLDER)
    assert f"Starting frames extraction process from '{TEST_INPUT_FOLDER}'..." in caplog.messages[0]


def test_extract_best_frames_from_all_videos_in_folder(evaluator):
    evaluator.filter_videos_from_files = Mock(return_value=[(TEST_VIDEO_PATH, TEST_VIDEO_FILENAME)])
    evaluator._extract_best_frames_from_video = Mock()
    evaluator.change_processed_video_name = Mock()

    evaluator.extract_best_frames_from_all_videos_in_folder(TEST_INPUT_FOLDER, TEST_VIDEO_EXTENSION,
                                                            TEST_NUMBER_OF_FRAMES, TEST_DONE_VIDEO_PREFIX)

    evaluator.filter_videos_from_files.assert_called_once_with(TEST_INPUT_FOLDER,
                                                               TEST_VIDEO_EXTENSION, TEST_DONE_VIDEO_PREFIX)
    evaluator._extract_best_frames_from_video.assert_called_once_with(TEST_VIDEO_PATH,
                                                                      TEST_NUMBER_OF_FRAMES)
    evaluator.change_processed_video_name.assert_called_once_with(TEST_INPUT_FOLDER, TEST_VIDEO_PATH,
                                                                  TEST_VIDEO_FILENAME, TEST_DONE_VIDEO_PREFIX)


def test_extract_best_frames_from_video(evaluator, caplog):
    evaluator.get_video_capture = Mock(return_value=TEST_CAP)
    evaluator.process_video_frames = Mock()
    evaluator.get_video_capture.return_value.release = TEST_CAP
    with caplog.at_level(logging.DEBUG):
        evaluator._extract_best_frames_from_video(TEST_VIDEO_PATH, TEST_NUMBER_OF_FRAMES)

    evaluator.get_video_capture.assert_called_once_with(TEST_VIDEO_PATH)
    evaluator.process_video_frames.assert_called_once_with(TEST_CAP,
                                                           TEST_NUMBER_OF_FRAMES)
    evaluator.get_video_capture.return_value.release.assert_called_once()
    assert f"Extracting best frames from video '{TEST_VIDEO_PATH}'..." in caplog.messages[0]


@pytest.mark.parametrize("invalid_number_of_frames", (-10, 0, 1))
def test_extract_best_frames_from_video_invalid_number_of_frame_to_compare(evaluator, caplog, invalid_number_of_frames):
    expected_message = (f"number_of_frames_to_compare must be bigger than 2. "
                        f"You provided: {invalid_number_of_frames}.")
    with pytest.raises(ValueError, match=expected_message), \
            caplog.at_level(logging.DEBUG):
        evaluator._extract_best_frames_from_video(TEST_VIDEO_PATH, invalid_number_of_frames)
        assert not caplog.messages


def test_process_video_frames(evaluator):
    mock_cap = create_autospec(cv2.VideoCapture, instance=True)
    mock_cap.isOpened.side_effect = [True, True, True, False]
    mock_cap.read.side_effect = [(True, 'frame1'), (True, 'frame2'), (True, 'frame3')]
    mock_cap.get.return_value = 1

    evaluator._get_best_frame = Mock()

    evaluator.process_video_frames(mock_cap, 2)

    assert evaluator._get_best_frame.call_count == 3
    evaluator._get_best_frame.assert_any_call('frame1', [], 2)
    evaluator._get_best_frame.assert_any_call('frame2', [], 2)
    evaluator._get_best_frame.assert_any_call('frame3', [], 2)


def test_process_video_frames_false_read_result(evaluator):
    mock_cap = create_autospec(cv2.VideoCapture, instance=True)
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, "")
    evaluator._get_best_frame = Mock()

    evaluator.process_video_frames(mock_cap, 2)

    mock_cap.isOpened.assert_called_once()
    mock_cap.read.assert_called_once()
    evaluator._get_best_frame.assert_not_called()


def test_extract_and_save_best_frame(evaluator, caplog):
    batch_frames = [(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8), 5.0)]
    evaluator._score_frame = Mock(return_value=10.0)
    evaluator.save_ndarray_frame = Mock()

    with caplog.at_level(logging.DEBUG):
        evaluator._get_best_frame(TEST_BGR_FRAME, batch_frames, 2)

    evaluator.save_ndarray_frame.assert_called_once_with(evaluator.output_folder, TEST_BGR_FRAME)
    assert f"Frame '{TEST_BGR_FRAME}' saved." in caplog.messages[0]
    assert not batch_frames


def test_change_processed_video_name(evaluator, caplog):
    expected_new_path = f"{TEST_INPUT_FOLDER}{TEST_DONE_VIDEO_PREFIX}{TEST_VIDEO_FILENAME}"
    with patch("app.best_frames_extractor.os.rename") as mock_rename, \
            caplog.at_level(logging.DEBUG):
        evaluator.change_processed_video_name(TEST_INPUT_FOLDER,
                                              TEST_VIDEO_PATH,
                                              TEST_VIDEO_FILENAME,
                                              TEST_DONE_VIDEO_PREFIX)
    assert f"Video path '{TEST_VIDEO_PATH}' changed to '{expected_new_path}'"
    mock_rename.assert_called_once_with(TEST_VIDEO_PATH, expected_new_path)


def test_get_video_capture_success(evaluator):
    mock_cap = create_autospec(cv2.VideoCapture, instance=True)
    with patch('app.best_frames_extractor.cv2.VideoCapture',
               return_value=mock_cap) as mock_cv2:
        mock_cv2.return_value.isOpened.return_value = True
        mock_cv2.return_value.release = MagicMock()
        result = evaluator.get_video_capture(TEST_VIDEO_PATH)
        assert result == mock_cap
    mock_cv2.assert_called_once_with(TEST_VIDEO_PATH)
    mock_cv2.return_value.isOpened.assert_called_once()
    mock_cv2.return_value.release.assert_not_called()


def test_get_video_capture_fail(evaluator):
    mock_cap = create_autospec(cv2.VideoCapture, instance=True)
    with patch('app.best_frames_extractor.cv2.VideoCapture',
               return_value=mock_cap) as mock_cv2:
        mock_cv2.return_value.isOpened.return_value = False
        mock_cv2.return_value.release = MagicMock()
        with pytest.raises(ValueError, match=f"Can't open: {TEST_VIDEO_PATH}"):
            result = evaluator.get_video_capture(TEST_VIDEO_PATH)
            assert not result
        mock_cv2.assert_called_once_with(TEST_VIDEO_PATH)
        mock_cv2.return_value.isOpened.assert_called_once()
        mock_cv2.return_value.release.assert_called_once()
