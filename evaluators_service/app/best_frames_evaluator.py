"""This module provides the BestFramesExtractor class, an implementation of the Evaluator
abstract class, used for extracting the best frames from video files in a given folder.

The module leverages OpenCV for video processing and numpy for numerical operations. It
includes functionalities to process multiple video files, filter them based on format and
processing status, and extract and save the best frames from each video.

Classes:
    BestFramesExtractor: Extracts best frames from video files.

How to Use:
    To use the BestFramesExtractor, instantiate it and call the `process` method with the
    path to the folder containing video files.
"""
from pathlib import Path
import logging
from typing import Generator

import cv2
import numpy as np

from .evaluator import Evaluator
from .image_rater import VideoManipulator
from .schemas import EvaluatorConfig

logger = logging.getLogger(__name__)


class BestFramesExtractor(Evaluator):
    files_extensions = (".mp4",)
    """A class derived from Evaluator that extracts the best frames from video files.

    This class scans a specified folder for video files and processes each video to
    extract and save the best frames based on a scoring mechanism defined in the Evaluator
    class. It filters video files based on their format and whether they have already
    been processed.
    """
    @classmethod
    def process(cls, config: EvaluatorConfig) -> None:
        """Process all videos in the given folder to extract best frames.

        Args:
            config (EvaluatorConfig): Path to the folder containing video files.
        """
        logger.info("Starting frames extraction process from '%s'...", config.input_directory)
        videos_paths = cls.list_directory_files(config.input_directory, config.videos_extension,
                                                config.processed_video_prefix)
        for video_path in videos_paths:
            frames = cls._extract_best_frames(video_path, config.frames_to_compare)
            cls._save_images(frames)
            cls._add_prefix(config.processed_video_prefix, video_path)

    @classmethod
    def _extract_best_frames(cls, video_path: Path, frames_to_compare: int) -> list[np.ndarray]:
        best_frames = []
        while True:
            frames = VideoManipulator.get_next_video_frames(video_path, frames_to_compare)
            if not frames:
                return best_frames
            best_frame = cls._get_best_image(frames)
            best_frames.append(best_frame)

    @staticmethod
    def _get_best_image(images: list[np.ndarray]) -> np.ndarray:
        """Extract and save the best frame from the batch.

            This method is designed to be called repeatedly for each frame in a video.
            It scores each frame and stores it in a batch. Once the batch reaches the
            specified size (number_of_frames_to_compare), the frame with the highest score
            is identified and saved. The batch is then cleared for the next set of frames.

        Args:
            bgr_frame (np.ndarray): The current frame from the video.
            batch_frames (list): List to store frames and their scores.
            number_of_frames_to_compare (int): Number of frames to compare to find the best one.
        """
        rated_images = .rate_images(images)
        best_image, _ = max(rated_images, key=lambda x: x[1])
        return best_image

    @staticmethod
    def _add_prefix(prefix: str, input_path: Path) -> Path:
        new_path = input_path.parent / f"{prefix}{input_path.name}"
        input_path.rename(new_path)
        logger.debug("Prefix '%s' added to file '%s'. New path: %s",
                     prefix, input_path, new_path)
        return new_path
