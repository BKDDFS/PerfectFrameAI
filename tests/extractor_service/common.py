"""Common fixtures for all conftest files."""
import pytest

from extractor_service.app.schemas import ExtractorConfig


@pytest.fixture(scope="package")
def config(files_dir, best_frames_dir) -> ExtractorConfig:
    config = ExtractorConfig(
        input_directory=files_dir,
        output_directory=best_frames_dir,
        images_output_format=".jpg",
        video_extensions=(".mp4",),
        processed_video_prefix="done_"
    )
    return config
