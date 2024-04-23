import concurrent
import logging
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from extractor_service.app.extractors import Extractor, ExtractorFactory, BestFramesExtractor, TopImagesExtractor
import extractor_service.app.image_raters as image_raters
from extractor_service.app.image_processors import OpenCVImage
from extractor_service.app.schemas import ExtractorConfig

current_directory = Path.cwd()
CONFIG = ExtractorConfig(
    input_directory=current_directory,
    output_directory=current_directory,
    images_output_format=".jpg"
)


class TestExtractor(Extractor):
    def process(self) -> None:
        pass


def test_extractor_initialization():
    extractor = TestExtractor(CONFIG)
    assert extractor is not None
    assert extractor.config == CONFIG
    assert extractor.image_rater is None


@pytest.fixture
def extractor():
    return TestExtractor(CONFIG)


def test_rate_images(extractor):
    test_input = MagicMock(spec=np.ndarray)
    expected = "expected"
    extractor.image_rater = MagicMock()
    extractor.image_rater.rate_images = MagicMock()
    extractor.image_rater.rate_images.return_value = expected

    result = extractor._rate_images(test_input)

    extractor.image_rater.rate_images.assert_called_once_with(test_input)
    assert result == expected


# def test_save_images(extractor):
#     OpenCVImage.save_image = MagicMock()
#     test_images = [MagicMock(spec=np.ndarray) for _ in range(3)]
#
#     with patch(
#             "concurrent.futures.ThreadPoolExecutor",
#             return_value=MagicMock(spec=ThreadPoolExecutor)
#     ) as mock_executor:
#         extractor._save_images(test_images)
#
#         mock_executor_instance = mock_executor.return_value.__enter__.return_value
#         assert mock_executor_instance.submit.call_count == len(test_images)
#
#     expected_calls = [
#         patch.call(
#             OpenCVImage.save_image,
#             image,
#             CONFIG.output_directory,
#             CONFIG.images_output_format
#         ) for image in test_images
#     ]
#     OpenCVImage.save_image.assert_has_calls(expected_calls, any_order=True)
#
#     for future in mock_executor_instance.submit.return_value:
#         assert future.result.called, "result was not called on future"


def test_add_prefix(extractor, caplog):
    test_prefix = "prefix_"
    test_path = Path("test_path\\file.mp4")
    test_new_path = Path("test_path\\prefix_file.mp4")
    expected_massage = f"Prefix '{test_prefix}' added to file '{test_path}'. New path: {test_new_path}"

    with patch("pathlib.Path.rename") as mock_rename, \
            caplog.at_level(logging.DEBUG):
        result = extractor._add_prefix(test_prefix, test_path)

        mock_rename.assert_called_once_with(test_new_path)
        assert expected_massage in caplog.text
    assert result == test_new_path


def test_display_info_after_extraction(extractor, caplog):
    expected_massage = "Press ctrl+c to exit."
    with caplog.at_level(logging.INFO):
        extractor._display_info_after_extraction()
        assert expected_massage in caplog.text

# @pytest.mark.parametrize("video_path, has_succeed", (
#         (TEST_VIDEO_PATH, True),
#         (f"{TEST_INPUT_FOLDER}done_video.mp4", False),
#         (f"{TEST_INPUT_FOLDER}video_done.mp4", True),
#         (f"{TEST_INPUT_FOLDER}videodone_.mp4", True),
# ))
# def test_filter_videos_from_files(evaluator, caplog, video_path, has_succeed):
#     available_extensions = (".avi", ".mp4", ".mov", ".webm", ".wmv", ".flv")
#     evaluator.get_files_with_specific_extension_from_folder = Mock(return_value=[video_path])
#     with caplog.at_level(logging.DEBUG):
#         result = list(evaluator.filter_videos_from_files(TEST_INPUT_FOLDER,
#                                                          TEST_VIDEO_EXTENSION, TEST_DONE_VIDEO_PREFIX))
#         evaluator.get_files_with_specific_extension_from_folder.assert_called_once_with(TEST_INPUT_FOLDER,
#                                                                                         TEST_VIDEO_EXTENSION,
#                                                                                         available_extensions)
#         if has_succeed:
#             file_name = os.path.basename(video_path)
#             assert f"Valid video found. Video: '{file_name}'." in caplog.messages[0]
#             assert (video_path, file_name) in result
#         else:
#             assert not caplog.messages
#             assert not result


def test_get_extractor_known_extractors():
    assert ExtractorFactory.get_extractor("best_frames_extractor") is BestFramesExtractor
    assert ExtractorFactory.get_extractor("top_images_extractor") is TopImagesExtractor


def test_get_extractor_unknown_extractor_raises(caplog):
    unknown_extractor_name = "unknown_extractor"
    expected_massage = f"Provided unknown extractor name: {unknown_extractor_name}"

    with pytest.raises(ValueError, match=expected_massage), \
            caplog.at_level(logging.ERROR):
        ExtractorFactory.get_extractor(unknown_extractor_name)

    assert expected_massage in caplog.text
