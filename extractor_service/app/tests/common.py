"""Common fixtures for all conftest files."""
import sys
from pathlib import Path

import pytest

from app.schemas import ExtractorConfig

common_path = Path(__file__).parent.parent.parent.parent / "common"
sys.path.insert(0, str(common_path))
from common import (
    files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)


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
