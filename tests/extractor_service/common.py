"""Common fixtures for all conftest files."""
import pytest

from extractor_service.app.dependencies import (ExtractorDependencies,
                                                get_evaluator,
                                                get_image_processor,
                                                get_video_processor)
from extractor_service.app.extractors import BestFramesExtractor
from extractor_service.app.schemas import ExtractorConfig


@pytest.fixture(scope="package")
def dependencies():
    image_processor = get_image_processor()
    video_processor = get_video_processor()
    evaluator = get_evaluator()

    return ExtractorDependencies(
        image_processor=image_processor,
        video_processor=video_processor,
        evaluator=evaluator
    )


@pytest.fixture(scope="package")
def extractor(config, dependencies):
    extractor = BestFramesExtractor(
        config, dependencies.image_processor,
        dependencies.video_processor, dependencies.evaluator
    )
    return extractor


@pytest.fixture(scope="package")
def config(files_dir, best_frames_dir) -> ExtractorConfig:
    config = ExtractorConfig(
        input_directory=files_dir,
        output_directory=best_frames_dir,
        images_output_format=".jpg",
        video_extensions=(".mp4",),
        processed_video_prefix="done_"
    )
    return config
