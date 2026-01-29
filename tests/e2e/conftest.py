"""E2E test fixtures using testcontainers."""

import os
import shutil
import time
from pathlib import Path

import pytest
import requests
from fastapi.testclient import TestClient
from testcontainers.compose import DockerCompose

from perfectframe.app import app
from tests.common import (
    best_frames_dir,
    config,
    files_dir,
    setup_best_frames_extractor_env,
    setup_top_images_extractor_env,
    top_images_dir,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"


@pytest.fixture(scope="package")
def client():
    with TestClient(app) as client:
        yield client


def wait_for_health(base_url: str, timeout: int = 120, interval: float = 0.5) -> bool:
    """Wait for health endpoint to return 200."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.ok:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
    return False


def wait_for_extraction_complete(base_url: str, timeout: int = 300, interval: float = 0.5) -> bool:
    """Wait for extraction to complete by polling /v2/status endpoint."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/v2/status", timeout=5)
            if response.ok:
                status = response.json()
                if status.get("active_extractor") is None:
                    return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
    return False


def cleanup_output_dir(output_dir: Path) -> None:
    """Remove all image files from output directory."""
    for f in output_dir.glob("image_*.jpg"):
        f.unlink()


@pytest.fixture(scope="package")
def extractor_service(tmp_path_factory):
    """Start extractor service using docker-compose."""
    input_dir = tmp_path_factory.mktemp("input")
    output_dir = tmp_path_factory.mktemp("output")

    # Copy test video to input (reset name if it was processed by another test)
    test_video = TEST_FILES_DIR / "test_video.mp4"
    processed_video = TEST_FILES_DIR / "frames_extracted_test_video.mp4"
    if processed_video.exists() and not test_video.exists():
        processed_video.rename(test_video)
    if test_video.exists():
        shutil.copy(test_video, input_dir / "test_video.mp4")

    # Copy test image to input (for top_images_extractor)
    test_image = TEST_FILES_DIR / "image_3e4aa2ce-7f83-45fd-b56f-e3bed645224e.jpg"
    if test_image.exists():
        shutil.copy(test_image, input_dir / "test_image.jpg")

    compose = DockerCompose(
        context=str(PROJECT_ROOT),
        compose_file_name="docker-compose.yaml",
        env_file=None,
        build=True,
    )
    # Set environment variables for volumes
    os.environ["INPUT_DIR"] = str(input_dir)
    os.environ["OUTPUT_DIR"] = str(output_dir)

    compose.start()

    # Wait for health endpoint
    base_url = "http://localhost:8100"
    if not wait_for_health(base_url):
        compose.stop()
        pytest.fail("Service did not become healthy in time")

    yield {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "base_url": base_url,
    }

    compose.stop()
    # Clean up environment variables
    os.environ.pop("INPUT_DIR", None)
    os.environ.pop("OUTPUT_DIR", None)
