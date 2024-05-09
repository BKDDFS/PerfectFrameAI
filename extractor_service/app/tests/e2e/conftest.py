from fastapi.testclient import TestClient
import pytest

from main import app, run_extractor
from ..common import (
    files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)  # import fixtures from common.py


@pytest.fixture(scope="package")
def client():
    with TestClient(app) as client:
        yield client
