import pytest

from extractor_service.app.extractors import BestFramesExtractor
from extractor_service.app.schemas import ExtractorConfig
from tests.extractor_service.common import extractor, config, dependencies
from tests.common import files_dir, best_frames_dir
