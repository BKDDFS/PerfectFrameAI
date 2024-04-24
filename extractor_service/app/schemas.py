"""This module defines models and validators for
managing evaluator processes in a frame evaluation application.
"""
import logging
from pathlib import Path

from pydantic import BaseModel, DirectoryPath

logger = logging.getLogger(__name__)


class ExtractorConfig(BaseModel):
    """A model for holding the request data for initiating an evaluation process.

    Attributes:
       input_directory (str):
            The path to the input folder containing data for evaluation.
       output_directory (str):
            The path to the output folder where evaluation results will be saved.
    """
    input_directory: DirectoryPath = Path("/app/input_directory")
    output_directory: DirectoryPath = Path("/app/output_directory")
    video_extensions: tuple[str] = (".mp4",)
    images_extensions: tuple[str] = (".jpg",)
    processed_video_prefix: str = "frames_extracted_"
    metric_model: str = "nima"
    compering_group_size: int = 5
    batch_size: int = 60
    top_images_percent: int = 90
    images_output_format: str = ".jpg"


class Message(BaseModel):
    """A simple model for encapsulating messages returned by the application.

    Attributes:
        message (str): The message content.
    """
    message: str


class ExtractorStatus(BaseModel):
    """A model representing the status of the current working evaluator in the system.

    Attributes:
        active_extractor (str):
            The name of the currently active evaluator or None if there is no active evaluator.
    """
    active_extractor: str | None
