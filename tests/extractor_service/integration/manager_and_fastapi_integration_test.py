from fastapi import BackgroundTasks
from starlette.testclient import TestClient

from extractor_service.app.extractor_manager import ExtractorManager
from extractor_service.main import app

client = TestClient(app)


def test_extractor_start_and_stop(config, dependencies):
    extractor_name = "best_frames_extractor"
    background_tasks = BackgroundTasks()

    response = ExtractorManager.start_extractor(extractor_name, background_tasks, config, dependencies)

    assert response == f"'{extractor_name}' started."
    assert ExtractorManager.get_active_extractor() is None
