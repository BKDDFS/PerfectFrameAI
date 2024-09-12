import pytest
from fastapi.testclient import TestClient

from extractor_service.main import app, run_extractor
from tests.common import (best_frames_dir, files_dir,
                          setup_best_frames_extractor_env,
                          setup_top_images_extractor_env, top_images_dir)
from tests.extractor_service.common import config


@pytest.fixture(scope="package")
def client():
    with TestClient(app) as client:
        yield client
