import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from app.extractors import (Extractor,
                            ExtractorFactory,
                            BestFramesExtractor,
                            TopImagesExtractor)


def test_extractor_initialization(config):
    extractor = BestFramesExtractor(config)
    assert extractor is not None
    assert extractor._config == config
    assert extractor._image_evaluator is None


@pytest.fixture
def extractor(config):
    return BestFramesExtractor(config)


@patch("app.extractors.InceptionResNetNIMA")
def test_get_image_evaluator(mock_evaluator, extractor, config):
    expected_evaluator = MagicMock()
    mock_evaluator.return_value = expected_evaluator

    result = extractor._get_image_evaluator()

    mock_evaluator.assert_called_once_with(config)
    assert result == expected_evaluator, \
        "The method did not return the correct ImageEvaluator instance."
    assert extractor._image_evaluator == expected_evaluator, \
        "The ImageEvaluator instance was not stored correctly in the extractor."


def test_evaluate_images(extractor):
    test_input = MagicMock(spec=np.ndarray)
    expected = "expected"
    extractor._image_evaluator = MagicMock()
    extractor._image_evaluator.evaluate_images = MagicMock()
    extractor._image_evaluator.evaluate_images.return_value = expected

    result = extractor._evaluate_images(test_input)

    extractor._image_evaluator.evaluate_images.assert_called_once_with(test_input)
    assert result == expected


@pytest.mark.parametrize("image", ("some_image", None))
@patch("app.extractors.OpenCVImage.read_image", return_value=None)
@patch("app.extractors.ThreadPoolExecutor")
def test_read_images(mock_executor, mock_read_image, image, extractor):
    mock_paths = [MagicMock(spec=Path) for _ in range(3)]
    mock_executor.return_value.__enter__.return_value = mock_executor
    mock_executor.submit.return_value.result.return_value = image
    calls = [
        ((mock_read_image, path),)
        for path in mock_paths
    ]

    result = extractor._read_images(mock_paths)

    assert mock_executor.submit.call_count == len(mock_paths)
    mock_executor.submit.assert_has_calls(calls, any_order=True)
    assert mock_executor.submit.return_value.result.call_count == len(mock_paths)
    if image:
        assert result
    else:
        assert not result


@patch("app.extractors.OpenCVImage.save_image", return_value=None)
@patch("app.extractors.ThreadPoolExecutor")
def test_save_images(mock_executor, mock_save_image, extractor, config):
    images = [MagicMock(spec=np.ndarray) for _ in range(3)]
    mock_executor.return_value.__enter__.return_value = mock_executor
    mock_executor.submit.return_value.result.return_value = None
    calls = [
        ((mock_save_image, image, config.output_directory, config.images_output_format),)
        for image in images
    ]

    extractor._save_images(images)

    assert mock_executor.submit.call_count == len(images)
    mock_executor.submit.assert_has_calls(calls, any_order=True)
    assert mock_executor.submit.return_value.result.call_count == len(images)


@patch.object(Path, "iterdir")
@patch.object(Path, "is_file")
def test_list_input_directory_files(mock_is_file, mock_iterdir, extractor, caplog, config):
    mock_files = [Path("/fake/directory/file1.txt"), Path("/fake/directory/file2.log")]
    mock_extensions = (".txt", ".log")
    mock_iterdir.return_value = mock_files
    mock_is_file.return_value = True

    with caplog.at_level(logging.DEBUG):
        result = extractor._list_input_directory_files(mock_extensions, None)

    assert result == mock_files
    assert f"Directory '{config.input_directory}' files listed." in caplog.text
    assert f"Listed file paths: {mock_files}"


@patch.object(Path, "iterdir")
def test_list_input_directory_files_no_files_found(mock_iterdir, extractor, caplog, config):
    mock_files = []
    mock_extensions = (".txt", ".log")
    mock_iterdir.return_value = mock_files
    error_massage = (
        f"Files with extensions '{mock_extensions}' and "
        f"without prefix 'Prefix not provided' not found in folder: {config.input_directory}."
        f"\n-->HINT: You probably don't have input or you haven't changed prefixes. "
        f"\nCheck input directory."
    )

    with pytest.raises(BestFramesExtractor.EmptyInputDirectoryError), \
            caplog.at_level(logging.ERROR):
        extractor._list_input_directory_files(mock_extensions)

    assert error_massage in caplog.text


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


def test_signal_readiness_for_shutdown(extractor, caplog):
    with caplog.at_level(logging.INFO):
        extractor._signal_readiness_for_shutdown()
    assert "Service ready for shutdown" in caplog.text


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
