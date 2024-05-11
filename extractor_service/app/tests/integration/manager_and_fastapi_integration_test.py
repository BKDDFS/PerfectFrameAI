from fastapi import BackgroundTasks
from starlette.testclient import TestClient

from app.extractor_manager import ExtractorManager
from app.schemas import ExtractorConfig
from main import app

client = TestClient(app)


def test_extractor_start_and_stop():
    extractor_name = "best_frames_extractor"
    background_tasks = BackgroundTasks()
    config = ExtractorConfig(parameters="example_parameters")

    response = ExtractorManager.start_extractor(background_tasks, config, extractor_name)

    assert response == f"'{extractor_name}' started."
    assert ExtractorManager.get_active_extractor() is None
