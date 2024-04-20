"""This module defines models and validators for
managing evaluator processes in a frame evaluation application.
"""
from pathlib import Path

from pydantic import BaseModel, model_validator


class ExtractorConfig(BaseModel):
    """A model for holding the request data for initiating an evaluation process.

    Attributes:
       input_directory (str):
            The path to the input folder containing data for evaluation.
       output_directory (str):
            The path to the output folder where evaluation results will be saved.
    """
    input_directory: str | Path = Path("/app/input_directory")
    output_directory: str | Path = Path("/app/output_directory")
    video_extensions: tuple[str] = (".mp4",)
    processed_video_prefix: str = "frames_extracted_"
    metric_model: str = "nima"
    compering_group_size: int = 5
    batch_size: int = 60
    top_image_threshold: int = 90

    @model_validator(mode="after")
    def validate_directory(self):
        """Validates that the directories are valid.

        Raises:
            NotADirectoryError: If the directory path is invalid.
        """
        directories = [Path(self.input_directory), Path(self.output_directory)]
        for directory in directories:
            if not directory.is_dir():
                raise NotADirectoryError(f"The path '{directory}' is not a directory.")
        return self


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
