"""This module provides the Evaluator abstract class, designed for video and image
evaluation tasks using various image quality assessment (IQA) metrics.

The module integrates functionalities from libraries such as OpenCV, PyTorch, Numpy,
and PyIQA, offering tools to process and evaluate image and video data. It supports
operations like converting image formats, applying transformations, scoring frames, and
saving results.

Classes:
    Evaluator: An abstract base class for creating specific evaluators for image and
               video analysis tasks, leveraging different IQA metrics and processing
               techniques.
"""
from pathlib import Path
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Evaluator(ABC):
    @abstractmethod
    def process(self, input_directory: str) -> None:
        """Abstract method to process video data.

        Args:
            input_directory: Arguments required for video processing.

        This method should be implemented by subclasses.
        """

    @staticmethod
    def list_directory_files(directory: Path, extensions: tuple[str], prefix: str) -> list[Path]:
        if not directory.is_dir():
            error_massage = f"Invalid directory: {directory}"
            logger.error(error_massage)
            raise NotADirectoryError(error_massage)
        entries = directory.iterdir()
        files = [
            entry for entry in entries
            if entry.is_file()
            and entry.suffix in extensions
            and not entry.name.startswith(prefix)
        ]
        if not files:
            logger.warning("Files with extensions '%s' and without prefix '%s' "
                           "not found in folder: '%s'", extensions, directory)
        return files
