"""This module defines models and validators for
managing evaluator processes in a frame evaluation application.

It includes:
- `EvaluatorStatus`:
    A model representing the current status of the evaluator,
    indicating whether an evaluation process is active.
- `RequestData`:
    A model for handling input and output folder paths for evaluation requests.
    It includes validators to ensure the existence and validity of these paths.
- `Message`:
    A simple model used to encapsulate and convey messages or
    responses within the application.
"""
import os
from typing import Optional

from pydantic import BaseModel, field_validator


class EvaluatorStatus(BaseModel):
    """A model representing the status of the current working evaluator in the system.

    Attributes:
        active_evaluator (str):
            The name of the currently active evaluator or None if there is no active evaluator.
    """
    active_evaluator: Optional[str]


class RequestData(BaseModel):
    """A model for holding the request data for initiating an evaluation process.

    Attributes:
       input_folder (str):
            The path to the input folder containing data for evaluation.
       output_folder (str):
            The path to the output folder where evaluation results will be saved.
    """
    input_folder: str
    output_folder: str

    @field_validator("input_folder")
    @classmethod
    def validate_input_folder(cls, input_folder) -> str:
        """Validates that the input folder exists and is a directory.

        Args:
            input_folder (str): The path to the input folder.

        Returns:
            str: The validated path to the input folder.

        Raises:
            NotADirectoryError: If the input folder path is not a directory.
        """
        if not os.path.isdir(input_folder):
            raise NotADirectoryError(f"The path '{input_folder}' is not a directory.")
        return input_folder

    @field_validator("output_folder")
    @classmethod
    def validate_output_folder(cls, output_folder) -> str:
        """
        Validates the output folder path and creates the directory if it does not exist.

        Args:
            output_folder (str): The path to the output folder.

        Returns:
            str: The validated or created path to the output folder.

        Raises:
            NotADirectoryError: If the path exists but is not a directory.
            OSError: If the directory could not be created.
        """
        if not os.path.isdir(output_folder):
            raise NotADirectoryError(f"The path '{output_folder}' is not a directory.")
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as error:
            raise OSError(f"Failed to create directory '{output_folder}': {error}") from error
        return output_folder


class Message(BaseModel):
    """A simple model for encapsulating messages returned by the application.

    Attributes:
        message (str): The message content.
    """
    message: str
