import logging
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

    # @staticmethod
    # @abstractmethod
    # def convert_bgr_image_to_rgb(bgr_image: np.ndarray) -> np.ndarray:
    #     pass

    @staticmethod
    @abstractmethod
    def save_image(image: np.ndarray, output_directory: Path,
                   output_filename: str, output_format: str = "jpg") -> Path:
        pass


class OpenCVImage(ImageProcessor):
    @staticmethod
    def read_image(image_path: Path) -> np.ndarray:
        image = cv2.imread(str(image_path))
        logger.debug("Image '%s' has successfully read.")
        return image

    # @staticmethod
    # def convert_bgr_image_to_rgb(bgr_frame: np.ndarray) -> np.ndarray:
    #     """Converts an image frame from BGR to RGB format.
    #
    #     Args:
    #         bgr_frame (np.ndarray): The image frame in BGR format.
    #
    #     Returns:
    #         np.ndarray: The converted image frame in RGB format.
    #
    #     """
    #     rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    #     logger.debug("Frame converted from BGR to RGB.")
    #     return rgb_frame

    @staticmethod
    def save_image(image: np.ndarray, output_directory: Path,
                   output_filename: str, output_format: str = ".jpg") -> Path:
        """Saves a ndarray image frame to a file in the specified format.

        Args:
            image (np.ndarray): The image frame in ndarray format to be saved.
            output_directory (str): The folder path where the image frame will be saved.
            output_filename (str):
            output_format (str): The format of the output file. Defaults to "jpg".

        Returns:
            Path: The file path of the saved image frame.
        """
        image_path = output_directory / f"{output_filename}{output_format}"
        cv2.imwrite(str(image_path), image)
        logger.debug("Image saved at '%s'.", image_path)
        return image_path
