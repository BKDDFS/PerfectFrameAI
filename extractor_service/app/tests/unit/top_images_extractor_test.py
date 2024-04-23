import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from extractor_service.app.extractors import TopImagesExtractor
from extractor_service.app.schemas import ExtractorConfig

current_directory = Path.cwd()
CONFIG = ExtractorConfig(
    input_directory=current_directory,
    output_directory=current_directory,
    images_extensions=(".jpg",)
)


@pytest.fixture
def extractor():
    extractor = TopImagesExtractor(CONFIG)
    return extractor


@patch('extractor_service.app.image_processors.OpenCVImage.read_image')
def test_process_with_images(mock_read_image, extractor, caplog):
    # Setup
    test_images = [
        "/fake/directory/image1.jpg", "/fake/directory/image2.jpg", "/fake/directory/image3.jpg"]
    test_ratings = [10, 20, 30]
    best_image = ["image3.jpg"]

    # Mock internal methods
    extractor._list_input_directory_files = MagicMock(return_value=test_images)
    extractor._get_image_rater = MagicMock()
    extractor._rate_images = MagicMock(return_value=test_ratings)
    extractor._get_top_percent_images = MagicMock(return_value=best_image)
    extractor._save_images = MagicMock()
    extractor._display_info_after_extraction = MagicMock()

    # Call
    with caplog.at_level(logging.INFO):
        extractor.process()

    # Check that the internal methods were called as expected
    extractor._list_input_directory_files.assert_called_once_with(
        extractor.config.images_extensions)
    mock_read_image.assert_has_calls([patch.call(path) for path in test_images])
    extractor._rate_images.assert_called_once_with([mock_read_image.return_value]*3)
    extractor._get_top_percent_images.assert_called_once_with(
        [mock_read_image.return_value]*3, test_ratings, extractor.config.top_images_percent)
    extractor._save_images.assert_called_once_with(best_image)

    # Check logging
    expected_massage = (
        f"Extraction process finished."
        f" All top images extracted from directory: {CONFIG.input_directory}."
    )
    assert expected_massage in caplog.text
    extractor._display_info_after_extraction.assert_called_once()