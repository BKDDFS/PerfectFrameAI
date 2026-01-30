"""Provide dependency management for extractors using FastAPI's dependency injection."""

from dataclasses import dataclass

from perfectframe.image_evaluators import NIMAEvaluator
from perfectframe.image_processors import OpenCVImage
from perfectframe.schemas import ExtractorConfig
from perfectframe.video_processors import OpenCVVideo


@dataclass
class Dependencies:
    """Data class to hold dependencies for the extractor."""

    image_processor: type[OpenCVImage]
    video_processor: type[OpenCVVideo]
    evaluator: type[NIMAEvaluator]
    config: ExtractorConfig


def get_dependencies(config: ExtractorConfig = ExtractorConfig()) -> Dependencies:
    """Return all dependencies required for the extractor."""
    return Dependencies(
        image_processor=OpenCVImage,
        video_processor=OpenCVVideo,
        evaluator=NIMAEvaluator,
        config=config,
    )
