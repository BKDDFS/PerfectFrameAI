import pytest

from extractor_service.app.extractors import BestFramesExtractor
from extractor_service.app.schemas import ExtractorConfig
from tests.extractor_service.common import config
from tests.common import files_dir, best_frames_dir


@pytest.fixture(scope="function")
def extractor(config):
    extractor = BestFramesExtractor(
        config, OpenCVImage, OpenCVVideo, InceptionResNetNIMA
    )
    return extractor
