from pathlib import Path

import pytest
from pydantic import ValidationError

from perfectframe.schemas import (
    ExtractorConfig,
    ExtractorName,
    ExtractorStatus,
    ImageExtension,
    Message,
    VideoExtension,
)


def test_config_default(mocker):
    mocker.patch.object(Path, "is_dir", return_value=True)
    config = ExtractorConfig()
    assert config.input_directory == Path("/app/input_directory")
    assert config.output_directory == Path("/app/output_directory")
    assert config.processed_video_prefix == "frames_extracted_"
    assert isinstance(config.compering_group_size, int)
    assert isinstance(config.batch_size, int)
    assert isinstance(config.top_images_percent, float)
    assert config.images_output_format == ImageExtension.JPG
    assert config.weights_directory == Path.home() / ".cache" / "huggingface"
    assert config.weights_filename == "weights.onnx"
    assert config.weights_repo_url == "https://huggingface.co/BKDDFS/nima_weights/resolve/main/"
    assert config.all_frames is False


def test_image_extension_contains():
    assert ImageExtension.contains(".jpg") is True
    assert ImageExtension.contains(".jpeg") is True
    assert ImageExtension.contains(".png") is True
    assert ImageExtension.contains(".webp") is True
    assert ImageExtension.contains(".mp4") is False
    assert ImageExtension.contains(".invalid") is False


def test_video_extension_contains():
    assert VideoExtension.contains(".mp4") is True
    assert VideoExtension.contains(".mov") is True
    assert VideoExtension.contains(".webm") is True
    assert VideoExtension.contains(".mkv") is True
    assert VideoExtension.contains(".avi") is True
    assert VideoExtension.contains(".jpg") is False
    assert VideoExtension.contains(".invalid") is False


def test_request_data_validation_failure_output():
    mock_directory = r"C:\invalid_dir"
    with pytest.raises(ValidationError):
        ExtractorConfig(input_directory=mock_directory)


def test_str_directory():
    mock_directory = str(Path.cwd())
    config = ExtractorConfig(input_directory=mock_directory)
    assert isinstance(config.input_directory, Path)


def test_extractor_status():
    status = ExtractorStatus(active_extractor=None)
    assert status.active_extractor is None

    status = ExtractorStatus(active_extractor=ExtractorName.BEST_FRAMES)
    assert status.active_extractor == ExtractorName.BEST_FRAMES


def test_message():
    mock_massage = "Test message"
    msg = Message(message=mock_massage)
    assert msg.message == mock_massage
