"""
This module provides abstract class for creating image processors and image processors.
Image processors:
    - OpenCVImage: using OpenCV library to manage operations on images.
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

    @staticmethod
    @abstractmethod
    def normalize_images(images: list[np.ndarray], target_size: tuple[int, int]) -> np.array:
        """
        Resize a batch of images and convert them to a normalized numpy array.

        Args:
            images (list[np.ndarray]): List of numpy ndarray images to be normalized.
            target_size (tuple | None): Target size to which the images will be resized.
                Default is (224, 224).

        Returns:
            np.ndarray: Normalized numpy array containing the resized images.
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
    def normalize_images(images: list[np.ndarray], target_size: tuple[int, int]) -> np.array:
        """
        Resize a batch of images and convert them to a normalized numpy array.

        Args:
            images (list[np.ndarray]): List of numpy ndarray images to be normalized.
            target_size (tuple | None): Target size to which the images will be resized.

        Returns:
            np.ndarray: Normalized numpy array containing the resized images.
        """
        batch_images = []
        logger.debug("Normalizing images...")
        for img in images:
            img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            batch_images.append(img_rgb)
        img_array = np.array(batch_images, dtype=np.float32) / 255.0
        return img_array
