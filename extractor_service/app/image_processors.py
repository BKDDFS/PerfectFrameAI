"""
This module provides abstract class for creating image processors and image processors.
Image processors:
    - OpenCVImage: using OpenCV library to manage operations on images.
"""
import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor(ABC):
    """Abstract class for creating image processors used for managing image operations."""
    @staticmethod
    @abstractmethod
    def read_image(image_path: Path) -> np.ndarray:
        """
        Read image from given path and convert it to np.ndarray.

        Args:
            image_path (Path): Path to image that will be read.

        Returns:
            np.ndarray: Image in numpy ndarray.
        """

    @classmethod
    @abstractmethod
    def save_image(cls, image: np.ndarray, output_directory: Path, output_extension: str) -> Path:
        """
        Save given image in given path in given extension.

        Args:
            image (np.ndarray): Numpy ndarray image that will be saved.
            output_directory (Path): Path where images will be saved.
            output_extension (str): Extension with image will be saved.

        Returns:
            Path: Path where image was saved.
        """


class OpenCVImage(ImageProcessor):
    """Image processor implementation using OpenCV library."""
    @staticmethod
    def read_image(image_path: Path) -> np.ndarray | None:
        """
        Read image from given path and convert it to np.ndarray.

        Args:
            image_path (Path): Path to image that will be read.

        Returns:
            np.ndarray: Image in numpy ndarray.
        """
        image = cv2.imread(str(image_path))
        if not isinstance(image, np.ndarray):
            logger.warning("Can't read image. OpenCV reading not returns np.ndarray for "
                           "image path: %s", str(image_path))
            return None
        logger.debug("Image '%s' has successfully read.", image_path)
        return image

    @classmethod
    def save_image(cls, image: np.ndarray, output_directory: Path, output_extension: str) -> Path:
        """
        Save given image in given path with given extension.

        Args:
            image (np.ndarray): Numpy ndarray image that will be saved.
            output_directory (Path): Path where images will be saved.
            output_extension (str): Extension with image will be saved.

        Returns:
            Path: Path where image was saved.
        """
        filename = cls._generate_filename()
        image_path = output_directory / f"{filename}{output_extension}"
        cv2.imwrite(str(image_path), image)
        logger.debug("Image saved at '%s'.", image_path)
        return image_path

    @staticmethod
    def _generate_filename() -> str:
        """
        Generate filename for images using uuid library.

        Returns:
            str: Generated filename.
        """
        filename = f"image_{uuid.uuid4()}"
        return filename

    @staticmethod
    def normalize_image(image: np.ndarray, target_size=(224, 224)) -> np.ndarray:
        """Resize an already loaded image and convert it to a normalized numpy array using OpenCV."""
        img_resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb.astype(np.float32) / 255.0
        img_batch = np.expand_dims(img_normalized, axis=0)
        return img_batch
