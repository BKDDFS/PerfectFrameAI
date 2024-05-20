import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.extractors import BestFramesExtractor
from app.video_processors import OpenCVVideo


@pytest.fixture(scope="function")
def extractor(config):
    extractor = BestFramesExtractor(config)
    return extractor


def test_process(extractor, caplog, config):
    test_videos = ["/fake/directory/video1.mp4", "/fake/directory/video2.mp4"]
    test_frames = ["frame1", "frame2"]
    extractor._list_input_directory_files = MagicMock(return_value=test_videos)
    extractor._get_image_evaluator = MagicMock()
    extractor._extract_best_frames = MagicMock(return_value=test_frames)
    extractor._save_images = MagicMock()
    extractor._add_prefix = MagicMock()
    extractor._signal_readiness_for_shutdown = MagicMock()

    with caplog.at_level(logging.INFO):
        extractor.process()

    extractor._list_input_directory_files.assert_called_once_with(
        config.video_extensions, config.processed_video_prefix)
    extractor._get_image_evaluator.assert_called_once()
    assert extractor._extract_best_frames.call_count == len(test_videos)
    assert extractor._save_images.call_count == len(test_videos)
    assert extractor._add_prefix.call_count == len(test_videos)
    extractor._signal_readiness_for_shutdown.assert_called_once()
    for video in test_videos:
        extractor._add_prefix.assert_any_call(config.processed_video_prefix, video)
        extractor._extract_best_frames.assert_any_call(video)
        extractor._save_images.assert_any_call(test_frames)
        assert f"Frames extraction has finished for video: {video}" in caplog.text
    assert f"Starting frames extraction process from '{config.input_directory}'." in caplog.text


@patch.object(OpenCVVideo, "get_next_frames")
@patch.object(BestFramesExtractor, "_normalize_images")
def test_extract_best_frames(mock_normalize, mock_get_next_frames, extractor, caplog):
    video_path = Path("/fake/video.mp4")
    frames_batch = [MagicMock() for _ in range(10)]
    frames_batch_1 = frames_batch
    frames_batch_2 = []
    frames_batch_3 = frames_batch
    mock_get_next_frames.return_value = iter([frames_batch_1, frames_batch_2, frames_batch_3])
    normalized_frames_1 = MagicMock(spec=np.ndarray)
    normalized_frames_2 = MagicMock(spec=np.ndarray)
    mock_normalize.side_effect = [normalized_frames_1, normalized_frames_2]
    test_ratings = [5, 6, 3, 8, 5, 2, 9, 1, 4, 7]
    extractor._evaluate_images = MagicMock(return_value=test_ratings)
    extractor._get_best_frames = MagicMock(
        side_effect=lambda frames, ratings, group_size: [frames[i] for i in [3, 6]])

    with caplog.at_level(logging.DEBUG):
        best_frames = extractor._extract_best_frames(video_path)

    mock_get_next_frames.assert_called_once_with(video_path, extractor._config.batch_size)
    assert extractor._evaluate_images.call_count == 2
    assert extractor._normalize_images.call_count == 2
    assert extractor._get_best_frames.call_count == 2
    assert len(best_frames) == 4
    extractor._evaluate_images.assert_any_call(normalized_frames_1)
    extractor._evaluate_images.assert_any_call(normalized_frames_2)
    for batch in [frames_batch_1, frames_batch_3]:
        extractor._get_best_frames.assert_any_call(
            batch,
            test_ratings,
            extractor._config.compering_group_size
        )
    assert caplog.text.count("Frames batch generated.") == 2


@pytest.fixture
def all_frames_extractor(extractor):
    extractor._config.all_frames = True
    yield extractor
    extractor._config.all_frames = False


def test_process_if_all_frames(extractor, caplog, config, all_frames_extractor):
    test_videos = ["/fake/directory/video1.mp4", "/fake/directory/video2.mp4"]
    test_frames = ["frame1", "frame2"]
    extractor._list_input_directory_files = MagicMock(return_value=test_videos)
    extractor._get_image_evaluator = MagicMock()
    extractor._extract_best_frames = MagicMock(return_value=test_frames)
    extractor._save_images = MagicMock()
    extractor._add_prefix = MagicMock()
    extractor._signal_readiness_for_shutdown = MagicMock()

    with caplog.at_level(logging.INFO):
        extractor.process()

    extractor._list_input_directory_files.assert_called_once_with(
        config.video_extensions, config.processed_video_prefix)
    extractor._get_image_evaluator.assert_not_called()
    assert not extractor._image_evaluator
    assert extractor._extract_best_frames.call_count == len(test_videos)
    assert extractor._save_images.call_count == len(test_videos)
    assert extractor._add_prefix.call_count == len(test_videos)
    extractor._signal_readiness_for_shutdown.assert_called_once()
    for video in test_videos:
        extractor._add_prefix.assert_any_call(config.processed_video_prefix, video)
        extractor._extract_best_frames.assert_any_call(video)
        extractor._save_images.assert_any_call(test_frames)
        assert f"Frames extraction has finished for video: {video}" in caplog.text
    assert f"Starting frames extraction process from '{config.input_directory}'." in caplog.text


@patch.object(BestFramesExtractor, "_evaluate_images")
@patch.object(BestFramesExtractor, "_get_best_frames")
@patch.object(OpenCVVideo, "get_next_frames")
@patch.object(BestFramesExtractor, "_normalize_images")
def test_extract_all_frames(mock_normalize, mock_get_next_frames,
                            mock_get, mock_evaluate, all_frames_extractor, caplog):
    video_path = Path("/fake/video.mp4")
    frames_batch = [MagicMock() for _ in range(3)]
    frames_batch_1 = frames_batch
    frames_batch_2 = []
    frames_batch_3 = frames_batch
    mock_get_next_frames.return_value = iter([frames_batch_1, frames_batch_2, frames_batch_3])

    with caplog.at_level(logging.DEBUG):
        best_frames = all_frames_extractor._extract_best_frames(video_path)

    mock_get_next_frames.assert_called_once_with(video_path, all_frames_extractor._config.batch_size)
    assert len(best_frames) == 6
    mock_evaluate.assert_not_called()
    mock_normalize.assert_not_called()
    mock_get.assert_not_called()
    assert caplog.text.count("Frames batch generated.") == 2


def test_get_best_frames(caplog, extractor):
    images = [MagicMock(spec=np.ndarray) for _ in range(10)]
    ratings = np.array([7, 2, 9, 3, 8, 5, 10, 1, 4, 6])
    batch_size = 3
    expected_best_images = [images[2], images[4], images[6], images[9]]

    with caplog.at_level(logging.INFO):
        best_images = extractor._get_best_frames(images, ratings, batch_size)

    assert best_images == expected_best_images
    assert f"Best frames selected({len(expected_best_images)})." in caplog.text
