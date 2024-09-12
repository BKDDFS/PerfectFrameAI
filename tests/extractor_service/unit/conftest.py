import pytest

from extractor_service.app.extractors import BestFramesExtractor
from extractor_service.app.schemas import ExtractorConfig
from tests.common import best_frames_dir, files_dir
from tests.extractor_service.common import config, dependencies, extractor
