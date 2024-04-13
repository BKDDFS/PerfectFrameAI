import logging
from unittest.mock import patch, MagicMock, Mock, call

import cv2
import numpy as np
import pytest

from app.top_frames_selector import (TopFramesSelector)

TEST_INPUT_FOLDER = "some/input/folder/path/"
TEST_OUTPUT_FOLDER = "some/output/folder/path/"
TEST_FRAME = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
TEST_SCORED_FRAMES = [(TEST_FRAME, 10.0), (TEST_FRAME, 1.0)]
TEST_PATHS = ["path1", "path2"]


@pytest.fixture(name="evaluator")
def best_frames_extractor_class_fixture() -> TopFramesSelector:
    with patch("app.evaluator.Evaluator.get_torch_device"), \
            patch("app.evaluator.Evaluator._check_folder_exists"):
        iqa_metric = MagicMock()
        transforms_compose = MagicMock()
        return TopFramesSelector(TEST_OUTPUT_FOLDER,
                                 iqa_metric=iqa_metric,
                                 transforms_compose=transforms_compose)


def test_process(evaluator):
    evaluator.load_frames = Mock(return_value=TEST_PATHS)
    evaluator.score_all_frames = Mock(return_value=TEST_SCORED_FRAMES)
    evaluator.save_top_frames = Mock()

    evaluator.process(TEST_INPUT_FOLDER)

    evaluator.load_frames.assert_called_once_with(TEST_INPUT_FOLDER)
    evaluator.score_all_frames.assert_called_once_with(TEST_PATHS)
    evaluator.save_top_frames.assert_called_once_with(TEST_SCORED_FRAMES)


def test_load_frames(evaluator, caplog):
    evaluator.get_files_with_specific_extension_from_folder = Mock(return_value=TEST_PATHS)

    with caplog.at_level(logging.DEBUG):
        result = evaluator.load_frames(TEST_INPUT_FOLDER)

    assert "Frames loaded." in caplog.messages[0]
    assert f"frame_paths: '{TEST_PATHS}'." in caplog.messages[1]
    assert result == TEST_PATHS


def test_score_all_frames(evaluator, caplog):
    test_frame = "some_frame"
    test_frame_score = 10.0
    cv2.imread = Mock(return_value=test_frame)
    evaluator._score_frame = Mock(return_value=test_frame_score)

    with caplog.at_level(logging.DEBUG):
        result = evaluator.score_all_frames(TEST_PATHS)

    assert cv2.imread.call_count == len(TEST_PATHS)
    assert evaluator._score_frame.call_count == len(TEST_PATHS)
    assert f"Frame '{TEST_PATHS[0]}' scored. Score: {test_frame_score}" in caplog.messages
    assert "Frames scored." in caplog.messages
    assert result == [(test_frame, test_frame_score), (test_frame, test_frame_score)]


def test_save_top_frames(evaluator, caplog):
    evaluator.save_ndarray_frame = Mock()

    with caplog.at_level(logging.DEBUG):
        evaluator.save_top_frames(TEST_SCORED_FRAMES)

    scores = [score for _, score in TEST_SCORED_FRAMES]
    threshold = np.percentile(scores, 90)

    expected_calls = [call(evaluator.output_folder, frame) for frame, score in TEST_SCORED_FRAMES if score > threshold]
    assert evaluator.save_ndarray_frame.mock_calls == expected_calls

    assert len(caplog.records) == 1
    assert "All top frames saved." in caplog.messages[0]
