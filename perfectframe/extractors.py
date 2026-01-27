"""Provide extractor classes for video and image processing.

- Extractor: Abstract class for creating extractors.
- ExtractorFactory: Factory for getting extractors by their names.
- Extractors:
    - BestFramesExtractor: For extracting best frames from all videos from any directory.
    - TopImagesExtractor: For extracting images with top percent evaluating from any directory.

LICENSE
=======
Copyright (C) 2024  Bartłomiej Flis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import gc
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from perfectframe.dependencies import ExtractorDependencies
from perfectframe.image_evaluators import ImageEvaluator
from perfectframe.image_processors import ImageProcessor
from perfectframe.schemas import ExtractorConfig, ExtractorName, Images, ImagesBatch, ScoresArray
from perfectframe.video_processors import VideoProcessor

logger = logging.getLogger(__name__)


class Extractor(ABC):
    """Abstract class for creating extractors."""

    class EmptyInputDirectoryError(Exception):
        """Error appear when extractor can't get any input to extraction."""

    def __init__(
        self,
        config: ExtractorConfig,
        image_processor: type[ImageProcessor],
        video_processor: type[VideoProcessor],
        image_evaluator_class: type[ImageEvaluator],
    ) -> None:
        """Initialize the manager with the given extractor configuration."""
        self._config = config
        self._image_processor = image_processor
        self._video_processor = video_processor
        self._image_evaluator_class = image_evaluator_class
        self._image_evaluator = None

    @abstractmethod
    def process(self) -> None:
        """Abstract main method for extraction process implementation."""

    def _get_image_evaluator(self) -> ImageEvaluator:
        """Initialize an image evaluator and add it to extractor instance parameters."""
        self._image_evaluator = self._image_evaluator_class(self._config)
        return self._image_evaluator

    def _list_input_directory_files(
        self,
        extensions: tuple[str, ...],
        prefix: str | None = None,
    ) -> list[Path]:
        """List all files with given extensions except files with given filename prefix.

        Args:
            extensions: Searched files extensions.
            prefix: Excluded files filename prefix.

        Returns:
            All matching files list.
        """
        directory = self._config.input_directory
        entries = directory.iterdir()
        files = [
            entry
            for entry in entries
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
        logger.info("Directory '%s' files listed.", str(directory))
        logger.debug("Listed file paths: %s", files)
        return files

    def _evaluate_images(self, normalized_images: ImagesBatch) -> ScoresArray:
        """Rate all images in provided images batch using already initialized image evaluator."""
        if self._image_evaluator is None:
            msg = "_image_evaluator must be initialized before calling _evaluate_images"
            raise RuntimeError(msg)
        return np.array(self._image_evaluator.evaluate_images(normalized_images))

    def _read_images(self, images_paths: list[Path]) -> Images:
        """Read all images from given paths synchronously."""
        with ThreadPoolExecutor() as executor:
            images = []
            futures = [
                executor.submit(
                    self._image_processor.read_image,
                    image_path,
                )
                for image_path in images_paths
            ]
            for future in futures:
                image = future.result()
                if image is not None:
                    images.append(image)
            return images

    def _save_images(self, images: Images) -> None:
        """Save all images in config output directory synchronously."""
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._image_processor.save_image,
                    image,
                    self._config.output_directory,
                    self._config.images_output_format,
                )
                for image in images
            ]
            for future in futures:
                future.result()

    def _normalize_images(self, images: Images, target_size: tuple[int, int]) -> ImagesBatch:
        """Normalize all images in given list to target size for further operations."""
        return self._image_processor.normalize_images(images, target_size)

    @staticmethod
    def _add_prefix(prefix: str, file_path: Path) -> Path:
        """Add prefix to file filename."""
        new_path = file_path.parent / f"{prefix}{file_path.name}"
        file_path.rename(new_path)
        logger.debug("Prefix '%s' added to file '%s'. New path: %s", prefix, file_path, new_path)
        return new_path

    @staticmethod
    def _signal_readiness_for_shutdown() -> None:
        """Signal externally that the service has completed the process and can be shut down."""
        logger.info("Service ready for shutdown")


class ExtractorFactory:
    """Extractor factory for getting extractors class by their names."""

    @staticmethod
    def create_extractor(
        extractor_name: ExtractorName,
        config: ExtractorConfig,
        dependencies: ExtractorDependencies,
    ) -> Extractor:
        """Match extractor class by its name and return its class."""
        match extractor_name:
            case ExtractorName.BEST_FRAMES:
                return BestFramesExtractor(
                    config,
                    dependencies.image_processor,
                    dependencies.video_processor,
                    dependencies.evaluator,
                )
            case ExtractorName.TOP_IMAGES:
                return TopImagesExtractor(
                    config,
                    dependencies.image_processor,
                    dependencies.video_processor,
                    dependencies.evaluator,
                )


class BestFramesExtractor(Extractor):
    """Extractor for extracting best frames from videos in any input directory."""

    def process(self) -> None:
        """Rate all videos in config input directory and extract best frames from every video."""
        logger.info(
            "Starting frames extraction process from '%s'.",
            self._config.input_directory,
        )
        videos_paths = self._list_input_directory_files(
            self._config.video_extensions, self._config.processed_video_prefix
        )
        if self._config.all_frames is False:  # evaluator won't be used if all frames
            self._get_image_evaluator()
        for video_path in videos_paths:
            self._extract_best_frames(video_path)
            self._add_prefix(self._config.processed_video_prefix, video_path)
            logger.info("Frames extraction has finished for video: %s", video_path)
        logger.info("Extraction process finished. All frames extracted.")
        self._signal_readiness_for_shutdown()

    def _extract_best_frames(self, video_path: Path) -> None:
        """Extract best visually frames from given video."""
        frames_batch_generator = self._video_processor.get_next_frames(
            video_path, self._config.batch_size
        )
        for frames in frames_batch_generator:
            if not frames:
                continue
            logger.debug("Frames batch generated.")
            frames_to_save = (
                self._get_best_frames(frames) if not self._config.all_frames else frames
            )
            self._save_images(frames_to_save)
            del frames_to_save
            gc.collect()

    def _get_best_frames(self, frames: Images) -> Images:
        """Split images batch into comparing groups and select best image for each group."""
        normalized_images = self._normalize_images(frames, self._config.target_image_size)
        scores = self._evaluate_images(normalized_images)
        del normalized_images

        best_frames = []
        group_size = self._config.compering_group_size
        groups = np.array_split(scores, np.arange(group_size, len(scores), group_size))
        for index, group in enumerate(groups):
            best_index = np.argmax(group)
            global_index = index * group_size + best_index
            best_frames.append(frames[global_index])
        logger.info("Best frames selected(%s).", len(best_frames))
        return best_frames


class TopImagesExtractor(Extractor):
    """Images extractor for extracting top percent of images in config input directory."""

    def process(self) -> None:
        """Rate all images in config input directory and extract top percent images."""
        images_paths = self._list_input_directory_files(self._config.images_extensions)
        self._get_image_evaluator()
        for batch_index in range(0, len(images_paths), self._config.batch_size):
            batch = images_paths[batch_index : batch_index + self._config.batch_size]
            images = self._read_images(batch)
            normalized_images = self._normalize_images(images, self._config.target_image_size)
            scores = self._evaluate_images(normalized_images)
            top_images = self._get_top_percent_images(
                images, scores, self._config.top_images_percent
            )
            self._save_images(top_images)
        logger.info(
            "Extraction process finished. All top images extracted from directory: %s.",
            self._config.input_directory,
        )
        self._signal_readiness_for_shutdown()

    @staticmethod
    def _get_top_percent_images(
        images: Images,
        scores: ScoresArray,
        top_percent: float,
    ) -> Images:
        """Return images that have scores in the top percent of all scores."""
        threshold = np.percentile(scores, top_percent)
        top_images = [img for img, score in zip(images, scores, strict=True) if score >= threshold]
        logger.info("Top images selected(%s).", len(top_images))
        return top_images
