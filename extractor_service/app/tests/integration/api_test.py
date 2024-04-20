import os
import shutil
import time

from fastapi.testclient import TestClient
import pytest
from main import app

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_get_evaluators_status_default(client):
    response = client.get("/frames_evaluators/status")
    assert response.status_code == 200
    assert response.json()["active_evaluator"] is None


@pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_extract_best_frames_and_get_evaluators_status(client):
    input_folder = os.path.join(CURRENT_DIRECTORY, "test_files")
    output_folder = os.path.join(CURRENT_DIRECTORY, "test_files/best_frames")
    video_path = os.path.join(input_folder, "test_video.mp4")

    # restart environment after previous test
    expected_video_path = os.path.join(input_folder, "frames_extracted_test_video.mp4")
    if os.path.isfile(expected_video_path):
        os.rename(expected_video_path, video_path)
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    assert not os.path.isdir(output_folder), "output_folder was not removed"
    os.makedirs(output_folder)

    request_data = {
        "input_folder": input_folder,
        "output_folder": output_folder
    }

    response = client.post("/frames_evaluators/best_frames_extractor", json=request_data)

    # check active evaluator
    status_response = client.get("/frames_evaluators/status")
    active_evaluator = status_response.json()["active_evaluator"]
    assert active_evaluator == "BestFramesExtractor"

    assert response.status_code == 200
    assert response.json()["message"] == f"'{active_evaluator}' started."

    # wait for evaluator work completion
    while client.get("/frames_evaluators/status").json()["active_evaluator"] is not None:
        time.sleep(1)


@pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_select_top_frames(client):
    input_folder = os.path.join(CURRENT_DIRECTORY, "test_files/best_frames")
    output_folder = os.path.join(CURRENT_DIRECTORY, "test_files/top_frames")

    # restart environment after previous test
    assert os.path.isdir(input_folder)
    files = os.listdir(input_folder)
    found_top_frame_files = [file for file in files if file.startswith("best_frame_") and file.endswith(".jpg")]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in OUTPUT_FOLDER"
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    assert not os.path.isdir(output_folder), "OUTPUT_FOLDER was not removed"
    os.makedirs(output_folder)

    request_data = {
        "input_folder": input_folder,
        "output_folder": output_folder
    }

    response = client.post("/frames_evaluators/top_frames_selector", json=request_data)

    # check active evaluator
    status_response = client.get("/frames_evaluators/status")
    active_evaluator = status_response.json()["active_evaluator"]
    assert active_evaluator == "TopFramesSelector"

    assert response.status_code == 200
    assert response.json()["message"] == f"'{active_evaluator}' started."

    # wait for evaluator work completion
    while client.get("/frames_evaluators/status").json()["active_evaluator"] is not None:
        time.sleep(1)
