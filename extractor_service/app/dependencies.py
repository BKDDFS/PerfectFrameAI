"""
This module provides dependency management for extractors using FastAPI's dependency injection.
LICENSE
=======
Copyright (C) 2024  Bartłomiej Flis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from dataclasses import dataclass
from typing import Type

from fastapi import Depends

from .image_evaluators import InceptionResNetNIMA
from .image_processors import OpenCVImage
from .video_processors import OpenCVVideo


@dataclass
class ExtractorDependencies:
    """
    Data class to hold dependencies for the extractor.

    Attributes:
        image_processor (Type[OpenCVImage]): Processor for image processing.
        video_processor (Type[OpenCVVideo]): Processor for video processing.
        evaluator (Type[InceptionResNetNIMA]): Evaluator for image quality.
    """
    image_processor: Type[OpenCVImage]
    video_processor: Type[OpenCVVideo]
    evaluator: Type[InceptionResNetNIMA]


def get_image_processor() -> Type[OpenCVImage]:
    """
    Provides the image processor dependency.

    Returns:
        Type[OpenCVImage]: The image processor class.
    """
    return OpenCVImage


def get_video_processor() -> Type[OpenCVVideo]:
    """
    Provides the video processor dependency.

    Returns:
        Type[OpenCVVideo]: The video processor class.
    """
    return OpenCVVideo


def get_evaluator() -> Type[InceptionResNetNIMA]:
    """
    Provides the image evaluator dependency.

    Returns:
        Type[InceptionResNetNIMA]: The image evaluator class.
    """
    return InceptionResNetNIMA


def get_extractor_dependencies(
        image_processor=Depends(get_image_processor),
        video_processor=Depends(get_video_processor),
        evaluator=Depends(get_evaluator)
) -> ExtractorDependencies:
    """
    Provides the dependencies required for the extractor.

    Args:
        image_processor (Type[OpenCVImage], optional): Dependency injection for image processor.
        video_processor (Type[OpenCVVideo], optional): Dependency injection for video processor.
        evaluator (Type[InceptionResNetNIMA], optional): Dependency injection for image evaluator.

    Returns:
        ExtractorDependencies: All necessary dependencies for the extractor.
    """
    return ExtractorDependencies(
        image_processor=image_processor,
        video_processor=video_processor,
        evaluator=evaluator
    )
