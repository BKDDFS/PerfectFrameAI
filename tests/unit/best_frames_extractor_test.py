import logging
from pathlib import Path

import numpy as np
import pytest
from pytest_mock import MockerFixture

from perfectframe.extractors import BestFramesExtractor
from perfectframe.image_evaluators import InceptionResNetNIMA
from perfectframe.image_processors import OpenCVImage
from perfectframe.video_processors import OpenCVVideo


@pytest.fixture
def all_frames_extractor(extractor):
    extractor._config.all_frames = True
    yield extractor
    extractor._config.all_frames = False


@pytest.fixture
def extractor(config):
    return BestFramesExtractor(config, OpenCVImage, OpenCVVideo, InceptionResNetNIMA)


def test_process(mocker: MockerFixture, extractor, caplog, config):
    test_videos = ["/fake/directory/video1.mp4", "/fake/directory/video2.mp4"]
    test_frames = ["frame1", "frame2"]
    extractor._list_input_directory_files = mocker.MagicMock(return_value=test_videos)
    extractor._get_image_evaluator = mocker.MagicMock()
    extractor._extract_best_frames = mocker.MagicMock(return_value=test_frames)
    extractor._add_prefix = mocker.MagicMock()
    extractor._signal_readiness_for_shutdown = mocker.MagicMock()

    with caplog.at_level(logging.INFO):
        extractor.process()

    extractor._list_input_directory_files.assert_called_once_with(
        config.video_extensions, config.processed_video_prefix
    )
    extractor._get_image_evaluator.assert_called_once()
    assert extractor._extract_best_frames.call_count == len(test_videos)
    assert extractor._add_prefix.call_count == len(test_videos)
    extractor._signal_readiness_for_shutdown.assert_called_once()
    for video in test_videos:
        extractor._add_prefix.assert_any_call(config.processed_video_prefix, video)
        extractor._extract_best_frames.assert_any_call(video)
        assert f"Frames extraction has finished for video: {video}" in caplog.text
    assert f"Starting frames extraction process from '{config.input_directory}'." in caplog.text


def test_process_if_all_frames(mocker: MockerFixture, all_frames_extractor, caplog, config):
    test_videos = ["/fake/directory/video1.mp4", "/fake/directory/video2.mp4"]
    test_frames = ["frame1", "frame2"]
    all_frames_extractor._list_input_directory_files = mocker.MagicMock(return_value=test_videos)
    all_frames_extractor._get_image_evaluator = mocker.MagicMock()
    all_frames_extractor._extract_best_frames = mocker.MagicMock(return_value=test_frames)
    all_frames_extractor._add_prefix = mocker.MagicMock()
    all_frames_extractor._signal_readiness_for_shutdown = mocker.MagicMock()

    with caplog.at_level(logging.INFO):
        all_frames_extractor.process()

    all_frames_extractor._list_input_directory_files.assert_called_once_with(
        config.video_extensions, config.processed_video_prefix
    )
    all_frames_extractor._get_image_evaluator.assert_not_called()
    assert not all_frames_extractor._image_evaluator
    assert all_frames_extractor._extract_best_frames.call_count == len(test_videos)
    assert all_frames_extractor._add_prefix.call_count == len(test_videos)
    all_frames_extractor._signal_readiness_for_shutdown.assert_called_once()
    for video in test_videos:
        all_frames_extractor._add_prefix.assert_any_call(config.processed_video_prefix, video)
        all_frames_extractor._extract_best_frames.assert_any_call(video)
        assert f"Frames extraction has finished for video: {video}" in caplog.text
    assert f"Starting frames extraction process from '{config.input_directory}'." in caplog.text


def test_extract_best_frames(mocker: MockerFixture, extractor):
    mock_generator = mocker.patch.object(OpenCVVideo, "get_next_frames")
    mock_save = mocker.patch.object(BestFramesExtractor, "_save_images")
    mock_get = mocker.patch.object(BestFramesExtractor, "_get_best_frames")
    mock_collect = mocker.patch("perfectframe.extractors.gc.collect")
    video_path = mocker.MagicMock(spec=Path)

    batch_1 = [f"frame{i}" for i in range(5)]
    batch_2 = []
    batch_3 = [f"frame{i}" for i in range(5)]
    mock_generator.return_value = iter([batch_1, batch_2, batch_3])

    mock_get.side_effect = [batch_1, batch_3]

    extractor._extract_best_frames(video_path)

    expected_call_count = 2
    assert not extractor._config.all_frames
    mock_generator.assert_called_once_with(video_path, extractor._config.batch_size)
    assert mock_get.call_count == expected_call_count
    for batch in [batch_1, batch_3]:
        mock_save.assert_called_with(batch)
    assert mock_collect.call_count == expected_call_count


def test_extract_all_frames(mocker: MockerFixture, all_frames_extractor):
    mock_generator = mocker.patch.object(OpenCVVideo, "get_next_frames")
    mock_save = mocker.patch.object(BestFramesExtractor, "_save_images")
    mock_get = mocker.patch.object(BestFramesExtractor, "_get_best_frames")
    mock_collect = mocker.patch("perfectframe.extractors.gc.collect")
    video_path = mocker.MagicMock(spec=Path)

    batch_1 = [f"frame{i}" for i in range(5)]
    batch_2 = []
    batch_3 = [f"frame{i}" for i in range(5)]
    mock_generator.return_value = iter([batch_1, batch_2, batch_3])

    all_frames_extractor._extract_best_frames(video_path)

    expected_call_count = 2
    assert all_frames_extractor._config.all_frames
    mock_generator.assert_called_once_with(video_path, all_frames_extractor._config.batch_size)
    assert mock_get.assert_not_called
    for batch in [batch_1, batch_3]:
        mock_save.assert_called_with(batch)
    assert mock_collect.call_count == expected_call_count


def test_get_best_frames(mocker: MockerFixture, caplog, extractor, config):
    mock_normalize = mocker.patch.object(BestFramesExtractor, "_normalize_images")
    mock_evaluate = mocker.patch.object(BestFramesExtractor, "_evaluate_images")
    frames = [f"frames{i}" for i in range(10)]
    scores = np.array([7, 2, 9, 3, 8, 5, 10, 1, 4, 6])
    normalized_images = [mocker.MagicMock() for _ in range(10)]
    mock_normalize.return_value = normalized_images
    mock_evaluate.return_value = scores
    expected_best_images = [frames[2], frames[6]]

    with caplog.at_level(logging.INFO):
        best_images = extractor._get_best_frames(frames)

    mock_evaluate.assert_called_once_with(normalized_images)
    mock_normalize.assert_called_once_with(frames, config.target_image_size)
    assert best_images == expected_best_images
    assert f"Best frames selected({len(expected_best_images)})." in caplog.text
