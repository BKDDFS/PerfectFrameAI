from fastapi import BackgroundTasks
from starlette.testclient import TestClient

from perfectframe.app import app
from perfectframe.extractor_manager import ExtractorManager
from perfectframe.schemas import ExtractorName, Message

client = TestClient(app)


def test_extractor_start_and_stop(dependencies):
    extractor_name = ExtractorName.BEST_FRAMES
    background_tasks = BackgroundTasks()

    response = ExtractorManager.start_extractor(extractor_name, background_tasks, dependencies)

    assert response == Message(message=f"'{extractor_name.value}' started.")
    assert ExtractorManager.get_active_extractor() == extractor_name
    ExtractorManager._active_extractor = None
