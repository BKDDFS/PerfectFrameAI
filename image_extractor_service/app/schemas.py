"""This module defines models and validators for
managing evaluator processes in a frame evaluation application.
"""
from pathlib import Path

from pydantic import BaseModel, field_validator


class ExtractorConfig(BaseModel):
    """A model for holding the request data for initiating an evaluation process.

    Attributes:
       input_directory (str):
            The path to the input folder containing data for evaluation.
       output_directory (str):
            The path to the output folder where evaluation results will be saved.
    """
    input_directory: Path
    output_directory: Path
    videos_extensions: tuple[str]
    processed_video_prefix: str = "frames_extracted_"
    model_name: str = "nima"
    comparing_group_size: int = 5
    processing_group_size: int = 50
    top_images_percent: int = 90

    @classmethod
    @field_validator("input_directory", "output_directory", mode="before")
    def validate_input_folder(cls, directory: Path) -> Path:
        """Validates that the directories are valid.

        Raises:
            NotADirectoryError: If the directory path is invalid.
        """
        if not directory.is_dir():
            raise NotADirectoryError(f"The path '{directory}' is not a directory.")
        return directory


class Message(BaseModel):
    """A simple model for encapsulating messages returned by the application.

    Attributes:
        message (str): The message content.
    """
    message: str


class EvaluatorStatus(BaseModel):
    """A model representing the status of the current working evaluator in the system.

    Attributes:
        active_evaluator (str):
            The name of the currently active evaluator or None if there is no active evaluator.
    """
    active_evaluator: str | None
