import pytest

from extractor_service.app.extractors import BestFramesExtractor
from tests.common import (best_frames_dir, files_dir,
                          setup_best_frames_extractor_env,
                          setup_top_images_extractor_env, top_images_dir)
from tests.extractor_service.common import config, dependencies, extractor
