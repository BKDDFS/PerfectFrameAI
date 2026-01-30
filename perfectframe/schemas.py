"""Define Pydantic models and validators."""

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

type Score = float
"""Single aesthetic score for an image."""

type Scores = list[Score]
"""List of aesthetic scores for images."""

type NIMAModelOutput = np.ndarray
"""NIMA model output: probability distribution over 10 aesthetic rating classes.

The model outputs 10 values representing the probability that an image
belongs to each aesthetic rating class (1-10). For example:
[0.01, 0.02, 0.03, 0.05, 0.15, 0.25, 0.25, 0.15, 0.07, 0.02]
means 1% chance for rating 1, 2% for rating 2, ..., 25% for rating 7, etc.
"""

type RatingScale = np.ndarray
"""Rating scale values [1, 2, 3, ..., 10] for calculating weighted mean.

Used to compute expected aesthetic rating from NIMAModelOutput:
final_score = sum(output * scale) / sum(scale)
"""


class ExtractorName(str, Enum):
    """Available extractor names."""

    BEST_FRAMES = "best_frames_extractor"
    TOP_IMAGES = "top_images_extractor"


class FileExtension(str, Enum):
    """Base class for file extension enums."""

    @classmethod
    def contains(cls, value: str) -> bool:
        """Check if value is a valid extension."""
        return value in cls._value2member_map_


class ImageExtension(FileExtension):
    """Supported image file extensions."""

    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    WEBP = ".webp"
    TIF = ".tif"
    TIFF = ".tiff"
    BMP = ".bmp"
    GIF = ".gif"


class VideoExtension(FileExtension):
    """Supported video file extensions."""

    MP4 = ".mp4"
    MOV = ".mov"
    WEBM = ".webm"
    MKV = ".mkv"
    AVI = ".avi"
    WMV = ".wmv"
    FLV = ".flv"
    M4V = ".m4v"


logger = logging.getLogger(__name__)


class ExtractorConfig(BaseModel):
    """A Pydantic model containing the extractors configuration parameters."""

    input_directory: DirectoryPath = Path("/app/input_directory")
    """Input directory path containing entries for extraction.

    By default, it sets value for docker container volume.
    """

    output_directory: DirectoryPath = Path("/app/output_directory")
    """Output directory path for extraction results.

    By default, it sets value for docker container volume.
    """

    processed_video_prefix: str = "frames_extracted_"
    """Prefix will be added to processed video after extraction."""

    batch_size: int = 100
    """Maximum number of images processed in a single batch."""

    comparing_group_size: int = 5
    """Images group number to compare for finding the best one."""

    top_images_percent: float = 90.0
    """Percentage threshold to determine the top images."""

    images_output_format: ImageExtension = ImageExtension.JPG
    """Format for saving output images."""

    input_size: ImageResolution = ImageResolution(224, 224)
    """Images will be normalized to this resolution for model input."""

    weights_directory: Path | str = Path.home() / ".cache" / "huggingface"
    """Directory path where model weights are stored."""

    weights_filename: str = "weights.onnx"
    """The filename of the model weights file to be loaded."""

    weights_repo_url: str = "https://huggingface.co/BKDDFS/nima_weights/resolve/main/"
    """URL to the repository where model weights can be downloaded."""

    all_frames: bool = False
    """It changes best_frames_extractor -> frames_extractor.

    If True best_frames_extractor returns all frames without filtering/evaluation.
    """


class Message(BaseModel):
    """A Pydantic model for encapsulating messages returned by the application."""

    message: str


class ExtractorStatus(BaseModel):
    """A Pydantic model representing the status of the currently working extractor in the system."""

    active_extractor: ExtractorName | None
