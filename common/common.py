"""Common fixtures for all conftest files."""
import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def files_dir():
    return Path(__file__).parent / "test_files"


@pytest.fixture(scope="session")
def best_frames_dir(files_dir):
    return files_dir / "best_frames"


@pytest.fixture(scope="session")
def top_images_dir(files_dir):
    return files_dir / "top_images"


@pytest.fixture(scope="function")
def setup_top_images_extractor_env(files_dir, top_images_dir) -> tuple[Path, Path]:
    assert files_dir.is_dir()

    # found_files = [file for file in files_dir.iterdir() if file.suffix == ".jpg"]
    # assert len(found_files) > 0, "No JPG files found in test directory"

    if top_images_dir.is_dir():
        shutil.rmtree(top_images_dir)
    assert not top_images_dir.is_dir(), "Output directory was not removed"
    top_images_dir.mkdir()

    return files_dir, top_images_dir


@pytest.fixture(scope="function")
def setup_best_frames_extractor_env(files_dir, best_frames_dir) -> tuple[Path, Path, Path]:
    video_filename = "test_video.mp4"
    expected_video_path = files_dir / f"frames_extracted_{video_filename}"
    video_path = files_dir / video_filename

    if expected_video_path.is_file():
        expected_video_path.rename(video_path)

    if best_frames_dir.is_dir():
        shutil.rmtree(best_frames_dir)
    assert not best_frames_dir.is_dir(), "Output directory was not removed"
    best_frames_dir.mkdir()
    assert best_frames_dir.is_dir(), "Output dir was not created after cleaning."

    return files_dir, best_frames_dir, expected_video_path
