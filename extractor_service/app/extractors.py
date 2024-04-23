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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from abc import ABC, abstractmethod
import logging
from typing import Type

import numpy as np

from .schemas import ExtractorConfig
from .video_processors import OpenCVVideo
from .image_processors import OpenCVImage
from .image_raters import PyIQA, ImageRater

logger = logging.getLogger(__name__)


class Extractor(ABC):
    class EmptyInputDirectoryError(Exception):
        pass

    def __init__(self, config: ExtractorConfig) -> None:
        self.config = config
        self.image_rater = None

    @abstractmethod
    def process(self) -> None:
        """Abstract method to process video data.
        """

    def _get_image_rater(self) -> ImageRater:
        self.image_rater = PyIQA(self.config.metric_model)
        return self.image_rater

    def _list_input_directory_files(self, extensions: tuple[str],
                                    prefix: str | None = None) -> list[Path]:
        directory = self.config.input_directory
        entries = directory.iterdir()
        files = [
            entry for entry in entries
            if entry.is_file()
            and entry.suffix in extensions
            and not entry.name.startswith(prefix) if prefix
        ]
        if not files:
            error_massage = (
                f"Files with extensions '{extensions}' and without prefix '{prefix}' "
                f"not found in folder: '{directory}'."
                f"\n-->HINT: You probably don't have input or you haven't changed prefixes. "
                f"\nCheck input directory."
            )
            logger.error(error_massage)
            raise self.EmptyInputDirectoryError(error_massage)
        logger.info(f"Directory '%s' files listed.", str(directory))
        logger.debug("Listed file paths: %s", files)
        return files

    def _rate_images(self, images: list[np.ndarray]) -> np.array:
        ratings = np.array(self.image_rater.rate_images(images))
        return ratings

    def _save_images(self, images: list[np.ndarray]):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                OpenCVImage.save_image, image,
                self.config.output_directory,
                self.config.images_output_format
            ) for image in images]
            for future in futures:
                future.result()

    @staticmethod
    def _add_prefix(prefix: str, input_path: Path) -> Path:
        new_path = input_path.parent / f"{prefix}{input_path.name}"
        input_path.rename(new_path)
        logger.debug("Prefix '%s' added to file '%s'. New path: %s",
                     prefix, input_path, new_path)
        return new_path

    @staticmethod
    def _display_info_after_extraction():
        logger.info("Press ctrl+c to exit.")


class ExtractorFactory:
    @staticmethod
    def get_extractor(extractor_name: str) -> Type[Extractor]:
        match extractor_name:
            case "best_frames_extractor":
                return BestFramesExtractor
            case "top_images_extractor":
                return TopImagesExtractor
            case _:
                error_massage = f"Provided unknown extractor name: {extractor_name}"
                logger.error(error_massage)
                raise ValueError(error_massage)


class BestFramesExtractor(Extractor):
    """A class derived from Evaluator that extracts the best frames from video files.

    This class scans a specified folder for video files and processes each video to
    extract and save the best frames based on a scoring mechanism defined in the Evaluator
    class. It filters video files based on their format and whether they have already
    been processed.
    """
    def process(self) -> None:
        """Process all videos in the given folder to extract the best frames.
        """
        logger.info("Starting frames extraction process from '%s'.",
                    self.config.input_directory)
        videos_paths = self._list_input_directory_files(self.config.video_extensions,
                                                        self.config.processed_video_prefix)
        self._get_image_rater()
        for video_path in videos_paths:
            frames = self._extract_best_frames(video_path)
            self._save_images(frames)
            self._add_prefix(self.config.processed_video_prefix, video_path)
            logger.info("Frames extraction has finished for video: %s", video_path)
        logger.info("Extraction process finished. All frames extracted.")
        self._display_info_after_extraction()

    def _extract_best_frames(self, video_path: Path) -> list[np.ndarray]:
        best_frames = []
        frames_generator = OpenCVVideo.get_next_video_frames(video_path, self.config.batch_size)
        for frames in frames_generator:
            if not frames:
                continue
            logger.debug("Frames pack generated.")
            ratings = self._rate_images(frames)
            selected_frames = self._get_best_images(frames, ratings,
                                                    self.config.compering_group_size)
            best_frames.extend(selected_frames)
        return best_frames

    @staticmethod
    def _get_best_images(images: list[np.ndarray], ratings: np.array,
                         batch_size: int) -> list[np.ndarray]:
        number_of_batches = (len(ratings) + batch_size - 1) // batch_size
        best_images = []
        for batch_index in range(number_of_batches):
            start_index = batch_index * batch_size
            end_index = start_index + batch_size
            batch_ratings = ratings[start_index:end_index]
            best_index = np.argmax(batch_ratings)
            best_images.append(images[start_index + best_index])
        logger.info("Best images selected.")
        return best_images


class TopImagesExtractor(Extractor):
    def process(self) -> None:
        images_paths = self._list_input_directory_files(self.config.images_extensions)
        self._get_image_rater()
        for batch_index in range(0, len(images_paths), self.config.batch_size):
            batch_paths = images_paths[batch_index:batch_index + self.config.batch_size]
            images = [OpenCVImage.read_image(path) for path in batch_paths]
            ratings = self._rate_images(images)
            top_images = self._get_top_percent_images(images, ratings,
                                                      self.config.top_images_percent)
            self._save_images(top_images)
        logger.info("Extraction process finished. All top images extracted from directory: %s.",
                    self.config.input_directory)
        self._display_info_after_extraction()

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
        logger.info("Top images selected.")
        return top_images
