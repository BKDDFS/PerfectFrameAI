"""
This module provides:
    - Extractor: Abstract class for creating extractors.
    - ExtractorFactory: Factory for getting extractors by their names.
    - Extractors:
        - BestFramesExtractor: For extracting best frames from all videos from any directory.
        - TopImagesExtractor: For extracting images with top percent evaluating from any directory.
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
from .image_evaluators import PyIQA

logger = logging.getLogger(__name__)


class Extractor(ABC):
    """Abstract class for creating extractors."""
    class EmptyInputDirectoryError(Exception):
        """Error appear when extractor can't get any input to extraction."""

    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initializes the manager with the given extractor configuration.

        Args:
            config (ExtractorConfig): A Pydantic model with configuration
                parameters for the extractor.
        """
        self._config = config
        self._image_evaluator = None

    @abstractmethod
    def process(self) -> None:
        """Abstract main method for extraction process implementation."""

    def _get_image_evaluator(self) -> PyIQA:
        """
        Initializes one of image evaluators (currently PyIQA) and
            adds it to extractor instance parameters.

        Returns:
            PyIQA: Image evaluator class instance for evaluating images.
        """
        self._image_evaluator = PyIQA(self._config.metric_model)
        return self._image_evaluator

    def _list_input_directory_files(self, extensions: tuple[str],
                                    prefix: str | None = None) -> list[Path]:
        """
        List all files with given extensions except files with given filename prefix form
            config input directory.

        Args:
            extensions (tuple): Searched files extensions.
            prefix (str | None): Excluded files filename prefix. Default is None.

        Returns:
            list: All matching files list.
        """
        directory = self._config.input_directory
        entries = directory.iterdir()
        files = [
            entry for entry in entries
            if entry.is_file()
            and entry.suffix in extensions
            and (prefix is None or not entry.name.startswith(prefix))
        ]
        if not files:
            prefix = prefix if prefix else "Prefix not provided"
            error_massage = (
                f"Files with extensions '{extensions}' and without prefix '{prefix}' "
                f"not found in folder: {directory}."
                f"\n-->HINT: You probably don't have input or you haven't changed prefixes. "
                f"\nCheck input directory."
            )
            logger.error(error_massage)
            raise self.EmptyInputDirectoryError(error_massage)
        logger.info(f"Directory '%s' files listed.", str(directory))
        logger.debug("Listed file paths: %s", files)
        return files

    def _evaluate_images(self, images: list[np.ndarray]) -> np.array:
        """
        Rating all images in provided images batch using already initialized image evaluator.

        Args:
            images (list): List of images in numpy ndarrays.

        Returns:
            np.array: Array with images scores in given images order.
        """
        scores = np.array(self._image_evaluator.evaluate_images(images))
        return scores

    @staticmethod
    def _read_images(paths: list[Path]) -> list[np.ndarray]:
        """
        Read all images from given paths synonymously.

        Args:
            paths: List of images paths.

        Returns:
            list: List of images in numpy ndarrays.
        """
        with ThreadPoolExecutor() as executor:
            images = []
            futures = [executor.submit(
                OpenCVImage.read_image, path,
            ) for path in paths]
            for future in futures:
                image = future.result()
                if image is not None:
                    images.append(image)
            return images

    def _save_images(self, images: list[np.ndarray]) -> None:
        """
        Save all images in config output directory synonymously.

        Args:
            images: List of images in numpy ndarrays.
        """
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                OpenCVImage.save_image, image,
                self._config.output_directory,
                self._config.images_output_format
            ) for image in images]
            for future in futures:
                future.result()

    @staticmethod
    def _add_prefix(prefix: str, path: Path) -> Path:
        """
        Adds prefix to file filename.
        
        Args:
            prefix: Prefix that will be added.
            path: Path to file that filename will be changed.

        Returns:
            Path: Path of the file with new filename.
        """
        new_path = path.parent / f"{prefix}{path.name}"
        path.rename(new_path)
        logger.debug("Prefix '%s' added to file '%s'. New path: %s",
                     prefix, path, new_path)
        return new_path

    @staticmethod
    def _display_info_after_extraction() -> None:
        """Display ending information for setup.py user after extraction process."""
        logger.info("Press ctrl+c to exit.")


class ExtractorFactory:
    """Extractor factory for getting extractors class by their names."""
    @staticmethod
    def get_extractor(extractor_name: str) -> Type[Extractor]:
        """
        Match extractor class by its name and return its class.

        Args:
            extractor_name (str): Name of the extractor that class will be returned.

        Returns:
            Extractor: Chosen extractor class.
        """
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
    """Extractor for extracting best frames from videos in any input directory."""
    def process(self) -> None:
        """
        Rate all videos in given config input directory and
        extract best visually frames from every video.
        """
        logger.info("Starting frames extraction process from '%s'.",
                    self._config.input_directory)
        videos_paths = self._list_input_directory_files(self._config.video_extensions,
                                                        self._config.processed_video_prefix)
        self._get_image_evaluator()
        for video_path in videos_paths:
            frames = self._extract_best_frames(video_path)
            self._save_images(frames)
            self._add_prefix(self._config.processed_video_prefix, video_path)
            logger.info("Frames extraction has finished for video: %s", video_path)
        logger.info("Extraction process finished. All frames extracted.")
        self._display_info_after_extraction()

    def _extract_best_frames(self, video_path: Path) -> list[np.ndarray]:
        """
        Extract best visually frames from given video.

        Args:
            video_path: Path of the video that will be extracted.

        Returns:
            list: List of best images(frames) in numpy ndarray from the given video.
        """
        best_frames = []
        frames_batch_generator = OpenCVVideo.get_next_video_frames(video_path, self._config.batch_size)
        for frames in frames_batch_generator:
            if not frames:
                continue
            logger.debug("Frames pack generated.")
            scores = self._evaluate_images(frames)
            selected_frames = self._get_best_images(frames, scores,
                                                    self._config.compering_group_size)
            best_frames.extend(selected_frames)
        return best_frames

    @staticmethod
    def _get_best_images(images: list[np.ndarray], scores: np.array,
                         comparing_group_size: int) -> list[np.ndarray]:
        """
        Splits images batch for comparing groups and select best image for each group.

        Args:
            images (list): Batch of images in numpy ndarray.
            scores (np.array): Array with images scores with images batch order.
            comparing_group_size (int): The size of the groups into which the batch will be divided.

        Returns:
            list: Best numpy ndarray images list.
        """
        best_images = []
        groups = np.array_split(scores, np.arange(comparing_group_size, len(scores), comparing_group_size))
        for index, group in enumerate(groups):
            best_index = np.argmax(group)
            global_index = index * comparing_group_size + best_index
            best_images.append(images[global_index])
        logger.info("Best images selected.")
        return best_images


class TopImagesExtractor(Extractor):
    """Extractor for extracting images that are in top percent of images in config input directory."""
    def process(self) -> None:
        """
        Rate all images in given config input directory and
        extract images that are in top percent of images visually.
        """
        images_paths = self._list_input_directory_files(self._config.images_extensions)
        self._get_image_evaluator()
        for batch_index in range(0, len(images_paths), self._config.batch_size):
            batch = images_paths[batch_index:batch_index + self._config.batch_size]
            images = self._read_images(batch)
            scores = self._evaluate_images(images)
            top_images = self._get_top_percent_images(images, scores,
                                                      self._config.top_images_percent)
            self._save_images(top_images)
        logger.info("Extraction process finished. All top images extracted from directory: %s.",
                    self._config.input_directory)
        self._display_info_after_extraction()

    @staticmethod
    def _get_top_percent_images(images: list[np.ndarray], scores: np.array,
                                top_percent: float) -> list[np.ndarray]:
        """
        Returns images that have scores in the top percent of all scores.

        Args:
            images (list): Batch of images in numpy ndarray.
            scores (list): Array with images scores with images batch order.
            top_percent (float): The top percentage of scores to include (e.g. 80 for top 80%).

        Returns:
            list: Top images from given images batch.
        """
        threshold = np.percentile(scores, top_percent)
        top_images = [img for img, score in zip(images, scores) if score > threshold]
        logger.info("Top images selected.")
        return top_images
