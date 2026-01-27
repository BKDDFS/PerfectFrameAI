"""Provide dependency management for extractors using FastAPI's dependency injection.

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

from fastapi import Depends

from perfectframe.image_evaluators import InceptionResNetNIMA
from perfectframe.image_processors import OpenCVImage
from perfectframe.video_processors import OpenCVVideo


@dataclass
class ExtractorDependencies:
    """Data class to hold dependencies for the extractor."""

    image_processor: type[OpenCVImage]
    video_processor: type[OpenCVVideo]
    evaluator: type[InceptionResNetNIMA]


def get_image_processor() -> type[OpenCVImage]:
    """Return the image processor dependency."""
    return OpenCVImage


def get_video_processor() -> type[OpenCVVideo]:
    """Return the video processor dependency."""
    return OpenCVVideo


def get_evaluator() -> type[InceptionResNetNIMA]:
    """Return the image evaluator dependency."""
    return InceptionResNetNIMA


def get_extractor_dependencies(
    image_processor: type[OpenCVImage] = Depends(get_image_processor),
    video_processor: type[OpenCVVideo] = Depends(get_video_processor),
    evaluator: type[InceptionResNetNIMA] = Depends(get_evaluator),
) -> ExtractorDependencies:
    """Return the dependencies required for the extractor."""
    return ExtractorDependencies(
        image_processor=image_processor,
        video_processor=video_processor,
        evaluator=evaluator,
    )
