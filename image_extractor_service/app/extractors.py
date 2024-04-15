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
import uuid
from pathlib import Path
from abc import ABC, abstractmethod
import logging

import numpy as np

from .schemas import ExtractorConfig
from .video_manipulators import OpenCVVideo
from .image_manipulators import OpenCVImage
from .image_rater import PyIQA

logger = logging.getLogger(__name__)


class Extractor(ABC):
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
        logger.debug("Listed file paths: %s", files)
        return files

    @staticmethod
    def _rate_images(images: list[np.ndarray], model_name: str) -> np.array:
        ratings = np.array(PyIQA.rate_images(images, model_name))
        return ratings

    @staticmethod
    def _save_images(images: list[np.ndarray], config: ExtractorConfig):
        for image in images:
            filename = f"image_{uuid.uuid4()}"
            OpenCVImage.save_image(image, config.output_directory, filename)

    @staticmethod
    def _add_prefix(prefix: str, input_path: Path) -> Path:
        new_path = input_path.parent / f"{prefix}{input_path.name}"
        input_path.rename(new_path)
        logger.debug("Prefix '%s' added to file '%s'. New path: %s",
                     prefix, input_path, new_path)
        return new_path


class BestFramesExtractor(Extractor):
    """A class derived from Evaluator that extracts the best frames from video files.

    This class scans a specified folder for video files and processes each video to
    extract and save the best frames based on a scoring mechanism defined in the Evaluator
    class. It filters video files based on their format and whether they have already
    been processed.
    """
    @classmethod
    def process(cls, config: ExtractorConfig) -> None:
        """Process all videos in the given folder to extract best frames.

        Args:
            config (EvaluatorConfig): Path to the folder containing video files.
        """
        logger.info("Starting frames extraction process from '%s'...", config.input_directory)
        videos_paths = cls.list_directory_files(config.input_directory, config.videos_extension,
                                                config.processed_video_prefix)
        for video_path in videos_paths:
            frames = cls._extract_best_frames(video_path, config.images_to_compare)
            images = [OpenCVImage.convert_bgr_image_to_rgb(frame) for frame in frames]
            cls._save_images(images, config)
            cls._add_prefix(config.processed_video_prefix, video_path)

    @classmethod
    def _extract_best_frames(cls, video_path: Path, config: ExtractorConfig) -> list[np.ndarray]:
        best_frames = []
        while True:
            frames = OpenCVVideo.get_next_video_frames(video_path, config.processing_group_size)
            if not frames:
                return best_frames
            ratings = cls._rate_images(frames, config.model_name)
            selected_frames = cls._get_best_images(frames, ratings, config.comparing_group_size)
            best_frames.extend(selected_frames)

    @staticmethod
    def _get_best_images(images: list[np.ndarray], ratings: np.array,
                         batch_size: int) -> list[np.ndarray]:
        number_of_batches = (len(ratings) + batch_size - 1) // batch_size
        best_images = []
        for i in range(number_of_batches):
            start_index = i * batch_size
            end_index = start_index + batch_size
            batch_ratings = ratings[start_index:end_index]
            best_index = np.argmax(batch_ratings)
            best_images.append(images[start_index + best_index])
        return best_images


class TopImagesExtractor(Extractor):
    @classmethod
    def process(cls, config: ExtractorConfig) -> None:
        images_paths = cls.list_directory_files(config.input_directory, config.images_extensions,
                                                config.processed_image_prefix)
        images = [OpenCVImage.read_image(path) for path in images_paths]
        ratings = cls._rate_images(images, config.model_name)
        top_images = cls._get_top_percent_images(images, ratings, config.top_images_percent)
        cls._save_images(top_images, config)
        logger.info("All top images saved.")

    @staticmethod
    def _get_top_percent_images(images: list[np.ndarray], ratings: np.array,
                                top_percent: float) -> list[np.ndarray]:
        """Returns images that have ratings in the top_percent of all ratings.

        Args:
            images (list[np.ndarray]): List of image arrays.
            ratings (list[float]): Corresponding ratings for each image.
            top_percent (float): The top percentage of ratings to include (e.g., 80 for top 80%).

        Returns:
            list[np.ndarray]: Images with ratings in the top X percent.
        """
        percentile_threshold = 100 - top_percent
        threshold = np.percentile(ratings, percentile_threshold)
        top_images = [img for img, rate in zip(images, ratings) if rate > threshold]
        return top_images
