import pytest

from ..common import (
    config, files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)  # import fixtures from common.py
from ...extractors import BestFramesExtractor


@pytest.fixture
def extractor(config):
    extractor = BestFramesExtractor(config)
    return extractor
