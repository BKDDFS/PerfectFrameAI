import logging
from unittest.mock import MagicMock, patch, call

import numpy as np
import pytest

from app.extractors import TopImagesExtractor
from app.image_processors import OpenCVImage


@pytest.fixture()
def extractor(config):
    extractor = TopImagesExtractor(config)
    return extractor


@patch.object(OpenCVImage, "read_image")
@patch.object(TopImagesExtractor, "_normalize_images")
def test_process_with_images(mock_normalize, mock_read_image, extractor, caplog, config):
    # Setup
    test_images = [
        "/fake/directory/image1.jpg", "/fake/directory/image2.jpg", "/fake/directory/image3.jpg"]
    test_ratings = [10, 20, 30]
    best_image = ["image3.jpg"]

    # Mock internal methods
    extractor._list_input_directory_files = MagicMock(return_value=test_images)
    extractor._get_image_evaluator = MagicMock()
    extractor._evaluate_images = MagicMock(return_value=test_ratings)
    extractor._get_top_percent_images = MagicMock(return_value=best_image)
    extractor._save_images = MagicMock()
    extractor._signal_readiness_for_shutdown = MagicMock()

    # Call
    with caplog.at_level(logging.INFO):
        extractor.process()

    # Check that the internal methods were called as expected
    extractor._list_input_directory_files.assert_called_once_with(
        extractor._config.images_extensions)
    mock_read_image.assert_has_calls([call(path) for path in test_images])
    mock_normalize.assert_called_once_with([mock_read_image.return_value]*3, extractor._config.target_image_size)
    extractor._evaluate_images.assert_called_once_with(mock_normalize.return_value)
    extractor._get_top_percent_images.assert_called_once_with(
        [mock_read_image.return_value]*3, test_ratings, extractor._config.top_images_percent)
    extractor._save_images.assert_called_once_with(best_image)

    # Check logging
    expected_massage = (
        f"Extraction process finished."
        f" All top images extracted from directory: {config.input_directory}."
    )
    assert expected_massage in caplog.text
    extractor._signal_readiness_for_shutdown.assert_called_once()


def test_get_top_percent_images(extractor, caplog):
    images = [MagicMock(spec=np.ndarray) for _ in range(5)]
    ratings = np.array([55, 70, 85, 40, 20])
    top_percent = 70
    expected_images = [images[1], images[2]]

    with caplog.at_level(logging.INFO):
        selected_images = extractor._get_top_percent_images(images, ratings, top_percent)

    assert selected_images == expected_images, "The selected images do not match the expected top percent images."
    assert f"Top images selected({len(expected_images)})." in caplog.text
