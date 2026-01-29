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
