"""Common fixtures for all conftest files."""

import shutil
from pathlib import Path

import pytest

from perfectframe.dependencies import (
    ExtractorDependencies,
    get_evaluator,
    get_image_processor,
    get_video_processor,
)
from perfectframe.extractors import BestFramesExtractor
from perfectframe.schemas import ExtractorConfig


@pytest.fixture(scope="session")
def files_dir():
    return Path(__file__).parent / "test_files"


@pytest.fixture(scope="session")
def best_frames_dir(files_dir):
    return files_dir / "best_frames"


@pytest.fixture(scope="session")
def top_images_dir(files_dir):
    return files_dir / "top_images"


@pytest.fixture
def setup_top_images_extractor_env(files_dir, top_images_dir):
    assert files_dir.is_dir()

    if top_images_dir.is_dir():
        shutil.rmtree(top_images_dir)
    assert not top_images_dir.is_dir(), "Output directory was not removed"
    top_images_dir.mkdir()

    yield files_dir, top_images_dir

    gitkeep_file = top_images_dir / ".gitkeep"
    gitkeep_file.touch()
    assert gitkeep_file.exists()


@pytest.fixture
def setup_best_frames_extractor_env(files_dir, best_frames_dir):
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

    yield files_dir, best_frames_dir, expected_video_path

    gitkeep_file = best_frames_dir / ".gitkeep"
    gitkeep_file.touch()
    assert gitkeep_file.exists()


@pytest.fixture(scope="package")
def dependencies():
    return ExtractorDependencies(
        image_processor=get_image_processor(),
        video_processor=get_video_processor(),
        evaluator=get_evaluator(),
    )


@pytest.fixture(scope="package")
def extractor(config, dependencies):
    return BestFramesExtractor(
        config,
        dependencies.image_processor,
        dependencies.video_processor,
        dependencies.evaluator,
    )


@pytest.fixture(scope="package")
def config(files_dir, best_frames_dir) -> ExtractorConfig:
    return ExtractorConfig(
        input_directory=files_dir,
        output_directory=best_frames_dir,
        images_output_format=".jpg",
        video_extensions=(".mp4",),
        processed_video_prefix="done_",
    )
