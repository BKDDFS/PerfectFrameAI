import pytest

from tests.extractor_service.common import extractor, config, dependencies
from tests.common import (
    files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)
from extractor_service.app.extractors import BestFramesExtractor
