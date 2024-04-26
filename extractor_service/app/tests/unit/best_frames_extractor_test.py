import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from extractor_service.app.extractors import BestFramesExtractor
from extractor_service.app.schemas import ExtractorConfig

current_directory = Path.cwd()
CONFIG = ExtractorConfig(
    input_directory=current_directory,
    output_directory=current_directory,
    images_output_format=".jpg",
    video_extensions=(".mp4",),
    processed_video_prefix="done_"
)


@pytest.fixture
def extractor():
    extractor = BestFramesExtractor(CONFIG)
    return extractor


def test_process(extractor, caplog):
    # Setup
    test_videos = ["/fake/directory/video1.mp4", "/fake/directory/video2.mp4"]
    test_frames = ["frame1", "frame2"]
    # Mock
    extractor._list_input_directory_files = MagicMock(return_value=test_videos)
    extractor._get_image_rater = MagicMock()
    extractor._extract_best_frames = MagicMock(return_value=test_frames)
    extractor._save_images = MagicMock()
    extractor._add_prefix = MagicMock()
    extractor._display_info_after_extraction = MagicMock()

    # Call
    with caplog.at_level(logging.INFO):
        extractor.process()

    # Verification
    extractor._list_input_directory_files.assert_called_once_with(
        CONFIG.video_extensions, CONFIG.processed_video_prefix)
    extractor._get_image_rater.assert_called_once()
    assert extractor._extract_best_frames.call_count == len(test_videos)
    assert extractor._save_images.call_count == len(test_videos)
    assert extractor._add_prefix.call_count == len(test_videos)
    extractor._display_info_after_extraction.assert_called_once()
    for video in test_videos:
        extractor._add_prefix.assert_any_call(CONFIG.processed_video_prefix, video)
        extractor._extract_best_frames.assert_any_call(video)
        extractor._save_images.assert_any_call(test_frames)

    # Logging
        assert f"Frames extraction has finished for video: {video}" in caplog.text
    assert f"Starting frames extraction process from '{CONFIG.input_directory}'." in caplog.text


@patch('extractor_service.app.video_processors.OpenCVVideo.get_next_video_frames')
def test_extract_best_frames(mock_get_next_video_frames, extractor, caplog):
    # Setup
    video_path = Path("/fake/video.mp4")
    frames_batch = [MagicMock() for _ in range(10)]
    frames_batch_1 = frames_batch
    frames_batch_2 = []
    frames_batch_3 = frames_batch
    mock_get_next_video_frames.return_value = iter([frames_batch_1, frames_batch_2, frames_batch_3])
    test_ratings = [5, 6, 3, 8, 5, 2, 9, 1, 4, 7]
    # Mock
    extractor._rate_images = MagicMock(return_value=test_ratings)
    extractor._get_best_images = MagicMock(
        side_effect=lambda frames, ratings, group_size: [frames[i] for i in [3, 6]])

    # Call
    with caplog.at_level(logging.DEBUG):
        best_frames = extractor._extract_best_frames(video_path)

    # Verification
    mock_get_next_video_frames.assert_called_once_with(video_path, extractor.config.batch_size)
    assert extractor._rate_images.call_count == 2
    assert extractor._get_best_images.call_count == 2
    assert len(best_frames) == 4
    extractor._rate_images.assert_any_call(frames_batch_1)
    extractor._rate_images.assert_any_call(frames_batch_3)
    for batch in [frames_batch_1, frames_batch_3]:
        extractor._get_best_images.assert_any_call(
            batch,
            test_ratings,
            extractor.config.compering_group_size
        )
    # Logging
    assert caplog.text.count("Frames pack generated.") == 2


def test_get_best_images(caplog, extractor):
    images = [MagicMock(spec=np.ndarray) for _ in range(10)]
    ratings = np.array([7, 2, 9, 3, 8, 5, 10, 1, 4, 6])
    batch_size = 3
    expected_best_images = [images[2], images[4], images[6], images[9]]

    with caplog.at_level(logging.INFO):
        best_images = extractor._get_best_images(images, ratings, batch_size)

    assert best_images == expected_best_images
    assert "Best images selected." in caplog.text
