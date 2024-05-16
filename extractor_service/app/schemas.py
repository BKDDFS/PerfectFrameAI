"""
This module defines Pydantic models and validators.
Models:
    - ExtractorConfig: Model containing the extractors configuration parameters.
    - Message: Model for encapsulating messages returned by the application.
    - ExtractorStatus: Model representing the status of the currently working extractor in the system.
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
from pathlib import Path

from pydantic import BaseModel, DirectoryPath

logger = logging.getLogger(__name__)


class ExtractorConfig(BaseModel):
    """
    A Pydantic model containing the extractors configuration parameters.

    Attributes:
        input_directory (DirectoryPath): Input directory path containing entries for extraction.
            By default, it sets value for docker container volume.
        output_directory (DirectoryPath): Output directory path where extraction results will be saved.
            By default, it sets value for docker container volume.
        video_extensions (tuple[str]): Supported videos' extensions in service for reading videos.
        images_extensions (tuple[str]): Supported images' extensions in service for reading images.
        processed_video_prefix (str): Prefix that will be added to processed video filename after extraction.
        batch_size (int): Maximum number of images processed in a single batch.
        compering_group_size (int): Maximum number of images in a group to compare for finding the best one.
        top_images_percent (float): Percentage threshold to determine the top images based on scores.
        images_output_format (str): Format for saving output images, e.g., '.jpg', '.png'.
        target_image_size (tuple[int, int]): Images will be normalized to this size.
        weights_directory (Path | str): Directory path where model weights are stored.
        weights_filename (str): The filename of the model weights file to be loaded.
        weights_repo_url (str): URL to the repository where model weights can be downloaded.
    """
    input_directory: DirectoryPath = Path("/app/input_directory")
    output_directory: DirectoryPath = Path("/app/output_directory")
    video_extensions: tuple[str] = (".mp4",)
    images_extensions: tuple[str] = (".jpg",)
    processed_video_prefix: str = "frames_extracted_"
    batch_size: int = 100
    compering_group_size: int = 5
    top_images_percent: float = 90.0
    images_output_format: str = ".jpg"
    target_image_size: tuple[int, int] = (224, 224)
    weights_directory: Path | str = Path.home() / ".cache" / "huggingface"
    weights_filename: str = "weights.h5"
    weights_repo_url: str = "https://huggingface.co/BKDDFS/nima_weights/resolve/main/"


class Message(BaseModel):
    """
    A Pydantic model for encapsulating messages returned by the application.

    Attributes:
        message (str): The message content.
    """
    message: str


class ExtractorStatus(BaseModel):
    """
    A Pydantic model representing the status of the currently working extractor in the system.

    Attributes:
        active_extractor (str): The name of the currently active extractor.
    """
    active_extractor: str | None
