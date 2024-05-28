from dataclasses import dataclass
from typing import Type

from fastapi import Depends

from .image_evaluators import InceptionResNetNIMA
from .image_processors import OpenCVImage
from .video_processors import OpenCVVideo


@dataclass
class ExtractorDependencies:
    image_processor: Type[OpenCVImage]
    video_processor: Type[OpenCVVideo]
    evaluator: Type[InceptionResNetNIMA]


def get_image_processor() -> Type[OpenCVImage]:
    return OpenCVImage


def get_video_processor() -> Type[OpenCVVideo]:
    return OpenCVVideo


def get_evaluator() -> Type[InceptionResNetNIMA]:
    return InceptionResNetNIMA


def get_extractor_dependencies(
        image_processor=Depends(get_image_processor),
        video_processor=Depends(get_video_processor),
        evaluator=Depends(get_evaluator)
) -> ExtractorDependencies:
    return ExtractorDependencies(
        image_processor=image_processor,
        video_processor=video_processor,
        evaluator=evaluator
    )
