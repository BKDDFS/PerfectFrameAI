"""Define Pydantic models and validators.

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

import logging
from enum import Enum
from pathlib import Path
from typing import NamedTuple

import numpy as np
from pydantic import BaseModel, DirectoryPath


class ImageResolution(NamedTuple):
    """Resolution of an image in pixels (width x height)."""

    width: int
    height: int


type Image = np.ndarray
"""Single image as numpy array."""

type Images = list[Image]
"""List of images."""

type ImagesBatch = np.ndarray
"""Batch of images as single numpy array for batch processing."""

type ScoresArray = np.ndarray
"""Array of aesthetic scores for images."""


class ExtractorName(str, Enum):
    """Available extractor names."""

    BEST_FRAMES = "best_frames_extractor"
    TOP_IMAGES = "top_images_extractor"


class ImageExtension(str, Enum):
    """Supported image file extensions."""

    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    WEBP = ".webp"

    @classmethod
    def contains(cls, value: str) -> bool:
        """Check if value is a valid extension."""
        return value in cls._value2member_map_


class VideoExtension(str, Enum):
    """Supported video file extensions."""

    MP4 = ".mp4"
    MOV = ".mov"
    WEBM = ".webm"
    MKV = ".mkv"
    AVI = ".avi"

    @classmethod
    def contains(cls, value: str) -> bool:
        """Check if value is a valid extension."""
        return value in cls._value2member_map_


logger = logging.getLogger(__name__)


class ExtractorConfig(BaseModel):
    """A Pydantic model containing the extractors configuration parameters.

    Attributes:
        input_directory (DirectoryPath): Input directory path containing entries for extraction.
            By default, it sets value for docker container volume.
        output_directory (DirectoryPath): Output directory path for extraction results.
            By default, it sets value for docker container volume.
        processed_video_prefix (str): Prefix will be added to processed video after extraction.
        batch_size (int): Maximum number of images processed in a single batch.
        compering_group_size (int): Images group number to compare for finding the best one.
        top_images_percent (float): Percentage threshold to determine the top images.
        images_output_format (ImageExtension): Format for saving output images.
        input_size (ImageResolution): Images will be normalized to this resolution for model input.
        weights_directory (Path | str): Directory path where model weights are stored.
        weights_filename (str): The filename of the model weights file to be loaded.
        weights_repo_url (str): URL to the repository where model weights can be downloaded.
        all_frames (bool): It changes best_frames_extractor -> frames_extractor.
            If Ture best_frames_extractor returns all frames without filtering/evaluation.
    """

    input_directory: DirectoryPath = Path("/app/input_directory")
    output_directory: DirectoryPath = Path("/app/output_directory")
    processed_video_prefix: str = "frames_extracted_"
    batch_size: int = 100
    compering_group_size: int = 5
    top_images_percent: float = 90.0
    images_output_format: ImageExtension = ImageExtension.JPG
    input_size: ImageResolution = ImageResolution(224, 224)
    weights_directory: Path | str = Path.home() / ".cache" / "huggingface"
    weights_filename: str = "weights.onnx"
    weights_repo_url: str = "https://huggingface.co/BKDDFS/nima_weights/resolve/main/"
    all_frames: bool = False


class Message(BaseModel):
    """A Pydantic model for encapsulating messages returned by the application."""

    message: str


class ExtractorStatus(BaseModel):
    """A Pydantic model representing the status of the currently working extractor in the system."""

    active_extractor: ExtractorName | None
