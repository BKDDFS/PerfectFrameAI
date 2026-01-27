from fastapi import BackgroundTasks
from starlette.testclient import TestClient

from perfectframe.app import app
from perfectframe.extractor_manager import ExtractorManager

client = TestClient(app)


def test_extractor_start_and_stop(config, dependencies):
    extractor_name = "best_frames_extractor"
    background_tasks = BackgroundTasks()

    response = ExtractorManager.start_extractor(
        extractor_name, background_tasks, config, dependencies
    )

    assert response == f"'{extractor_name}' started."
    assert ExtractorManager.get_active_extractor() is None
