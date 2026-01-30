import logging
from pathlib import Path

import numpy as np
import pytest

from perfectframe.extractors import (
    BestFramesExtractor,
    ExtractorFactory,
    TopImagesExtractor,
)
from perfectframe.image_processors import OpenCVImage
from perfectframe.schemas import ExtractorName, VideoExtension


def test_extractor_initialization(config, dependencies):
    extractor = BestFramesExtractor(
        config,
        dependencies.image_processor,
        dependencies.video_processor,
        dependencies.evaluator,
    )
    assert extractor
    assert extractor._config == config
    assert extractor._image_evaluator is None


def test_get_image_evaluator(mocker, extractor, config):
    expected = "value"
    mock_class = mocker.MagicMock(return_value=expected)
    extractor._image_evaluator_class = mock_class

    result = extractor._get_image_evaluator()

    mock_class.assert_called_once_with(config)
    assert result == expected, "The method did not return the correct ImageEvaluator instance."
    assert extractor._image_evaluator == expected, (
        "The ImageEvaluator instance was not stored correctly in the extractor."
    )


def test_evaluate_images(mocker, extractor):
    test_input = mocker.MagicMock(spec=np.ndarray)
    expected = "expected"
    extractor._image_evaluator = mocker.MagicMock()
    extractor._image_evaluator.evaluate_images = mocker.MagicMock()
    extractor._image_evaluator.evaluate_images.return_value = expected

    result = extractor._evaluate_images(test_input)

    extractor._image_evaluator.evaluate_images.assert_called_once_with(test_input)
    assert result == expected


def test_evaluate_images_raises_when_evaluator_not_initialized(mocker, extractor):
    test_input = mocker.MagicMock(spec=np.ndarray)
    extractor._image_evaluator = None

    with pytest.raises(RuntimeError, match="_image_evaluator must be initialized"):
        extractor._evaluate_images(test_input)


@pytest.mark.parametrize("image", ["some_image", None])
def test_read_images(mocker, image, extractor):
    mock_executor = mocker.patch("perfectframe.extractors.ThreadPoolExecutor")
    mock_read_image = mocker.patch.object(OpenCVImage, "read_image", return_value=None)
    mock_paths = [mocker.MagicMock(spec=Path) for _ in range(3)]
    mock_executor.return_value.__enter__.return_value = mock_executor
    mock_executor.submit.return_value.result.return_value = image
    calls = [((mock_read_image, path),) for path in mock_paths]

    result = extractor._read_images(mock_paths)

    assert mock_executor.submit.call_count == len(mock_paths)
    mock_executor.submit.assert_has_calls(calls, any_order=True)
    assert mock_executor.submit.return_value.result.call_count == len(mock_paths)
    if image:
        assert result
    else:
        assert not result


def test_save_images(mocker, extractor, config):
    mock_executor = mocker.patch("perfectframe.extractors.ThreadPoolExecutor")
    mocker.patch.object(OpenCVImage, "read_image", return_value=None)
    images = [mocker.MagicMock(spec=np.ndarray) for _ in range(3)]
    mock_executor.return_value.__enter__.return_value = mock_executor
    mock_executor.submit.return_value.result.return_value = None
    calls = [
        (
            (
                OpenCVImage.save_image,
                image,
                config.output_directory,
                config.images_output_format,
            ),
        )
        for image in images
    ]

    extractor._save_images(images)

    assert mock_executor.submit.call_count == len(images)
    mock_executor.submit.assert_has_calls(calls, any_order=True)
    assert mock_executor.submit.return_value.result.call_count == len(images)


def test_normalize_images(mocker, extractor, config):
    mock_normalize = mocker.patch.object(OpenCVImage, "normalize_images")
    images = [mocker.MagicMock() for _ in range(3)]

    extractor._normalize_images(images, config.input_size)

    mock_normalize.assert_called_once_with(images, config.input_size)


def test_list_input_directory_files(mocker, extractor, caplog, config):
    mock_iterdir = mocker.patch.object(Path, "iterdir")
    mock_is_file = mocker.patch.object(Path, "is_file")
    mock_files = [Path("/fake/directory/file1.mp4"), Path("/fake/directory/file2.mov")]
    mock_iterdir.return_value = mock_files
    mock_is_file.return_value = True

    with caplog.at_level(logging.DEBUG):
        result = extractor._list_input_directory_files(VideoExtension, None)

    assert result == mock_files
    assert f"Directory '{config.input_directory}' files listed." in caplog.text
    assert f"Listed file paths: {mock_files}" in caplog.text


def test_list_input_directory_files_no_files_found(mocker, extractor, caplog):
    mock_iterdir = mocker.patch.object(Path, "iterdir")
    mock_files = []
    mock_iterdir.return_value = mock_files

    with (
        pytest.raises(BestFramesExtractor.EmptyInputDirectoryError),
        caplog.at_level(logging.ERROR),
    ):
        extractor._list_input_directory_files(VideoExtension)

    assert "not found in folder" in caplog.text
    assert "without prefix 'Prefix not provided'" in caplog.text


def test_add_prefix(mocker, extractor, caplog):
    mock_rename = mocker.patch("pathlib.Path.rename")
    test_prefix = "prefix_"
    test_path = Path("test_path/file.mp4")
    test_new_path = Path("test_path/prefix_file.mp4")
    expected_message = (
        f"Prefix '{test_prefix}' added to file '{test_path}'. New path: {test_new_path}"
    )

    with caplog.at_level(logging.DEBUG):
        result = extractor._add_prefix(test_prefix, test_path)

    mock_rename.assert_called_once_with(test_new_path)
    assert expected_message in caplog.text
    assert result == test_new_path


def test_signal_readiness_for_shutdown(extractor, caplog):
    with caplog.at_level(logging.INFO):
        extractor._signal_readiness_for_shutdown()
    assert "Service ready for shutdown" in caplog.text


@pytest.mark.parametrize(
    ("extractor_name", "extractor_class"),
    [
        (ExtractorName.BEST_FRAMES, BestFramesExtractor),
        (ExtractorName.TOP_IMAGES, TopImagesExtractor),
    ],
)
def test_create_extractor_known_extractors(extractor_name, extractor_class, dependencies):
    extractor_instance = ExtractorFactory.create_extractor(extractor_name, dependencies)
    assert isinstance(extractor_instance, extractor_class)
