from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.schemas import ExtractorConfig, Message, ExtractorStatus


def test_config_default():
    with patch('pathlib.Path.is_dir', return_value=True):
        config = ExtractorConfig()
    assert config.input_directory == Path("/app/input_directory")
    assert config.output_directory == Path("/app/output_directory")
    assert config.video_extensions == (".mp4",)
    assert config.images_extensions == (".jpg",)
    assert config.processed_video_prefix == "frames_extracted_"
    assert config.metric_model == "nima"
    assert config.compering_group_size == 5
    assert config.batch_size == 60
    assert config.top_images_percent == 90
    assert config.images_output_format == ".jpg"


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

    mock_status = "BestFramesExtractor"
    status = ExtractorStatus(active_extractor=mock_status)
    assert status.active_extractor == mock_status


def test_message():
    mock_massage = "Test message"
    msg = Message(message=mock_massage)
    assert msg.message == mock_massage
