from typing import Type

from .image_evaluators import InceptionResNetNIMA
from .image_processors import OpenCVImage
from .video_processors import OpenCVVideo


def get_image_processor() -> Type[OpenCVImage]:
    return OpenCVImage


def get_video_processor() -> Type[OpenCVVideo]:
    return OpenCVVideo


def get_evaluator() -> Type[InceptionResNetNIMA]:
    return InceptionResNetNIMA
