import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor(ABC):
    @staticmethod
    @abstractmethod
    def read_image(image_path: Path) -> np.ndarray:
        pass

    @staticmethod
    @abstractmethod
    def save_image(image: np.ndarray, output_directory: Path, output_format: str) -> Path:
        pass


class OpenCVImage(ImageProcessor):
    @staticmethod
    def read_image(image_path: Path) -> np.ndarray:
        image = cv2.imread(str(image_path))
        logger.debug("Image '%s' has successfully read.")
        return image

    @classmethod
    def save_image(cls, image: np.ndarray, output_directory: Path, output_format: str) -> Path:
        """Saves a ndarray image frame to a file in the specified format.

        Args:
            image (np.ndarray): The image frame in ndarray format to be saved.
            output_directory (str): The folder path where the image frame will be saved.
            output_format (str): The format of the output file.

        Returns:
            Path: The file path of the saved image frame.
        """
        filename = cls._generate_filename()
        image_path = output_directory / f"{filename}{output_format}"
        cv2.imwrite(str(image_path), image)
        logger.debug("Image saved at '%s'.", image_path)
        return image_path

    @staticmethod
    def _generate_filename() -> str:
        filename = f"image_{uuid.uuid4()}"
        return filename
