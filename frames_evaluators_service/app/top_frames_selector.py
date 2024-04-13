"""This module provides the TopFramesSelector class
for selecting the top frames from a series of images.
It is designed for image and video evaluation tasks that
require identifying and processing the most significant frames based on
specific image quality assessment (IQA) metrics.

Classes:
    TopFramesSelector: Extends the Evaluator class to select and
    process the top frames from a set of images. It includes methods
    for loading frames from a specified folder, scoring each frame using
    IQA metrics, and saving the top-scored frames based on a percentile threshold.

Usage:
    This class is intended to be used in scenarios where it's crucial to
    identify and process the most significant or highest quality frames from a
    collection of images, such as in video analysis, quality control in image processing,
    or content curation in media applications.
"""
import logging

import cv2
import numpy as np

from app.evaluator import Evaluator

logger = logging.getLogger(__name__)


class TopFramesSelector(Evaluator):
    """The TopFramesSelector class extends
    the Evaluator class, focusing on selecting and
    processing the top frames from a series of images
    based on image quality assessment (IQA) metrics.

    Attributes:
        Inherits all attributes from the Evaluator class.

    Methods:
        process(input_folder): Processes frames in the specified input folder.
        load_frames(frames_folder, frames_extension): Loads
            frame paths from a folder with a specific file extension.
        score_all_frames(frame_paths): Scores each frame based on a defined criteria.
        save_top_frames(scored_frames, threshold_percentile): Saves the
            top frames based on their scores and a threshold percentile.
    """
    def process(self, input_folder: str) -> None:
        """Process the frames in the specified input folder.

        Args:
            input_folder (str): The path to the folder containing frames to process.
        """
        frame_paths = self.load_frames(input_folder)
        scored_frames = self.score_all_frames(frame_paths)
        self.save_top_frames(scored_frames)

    def load_frames(self, frames_folder: str, frames_extension: str = ".jpg") -> list[str]:
        """Load frame paths from a specified folder with a specific file extension.

        Args:
            frames_folder (str): The folder from which to load frames.
            frames_extension (str): The file extension of the frames to load. Defaults to ".jpg".

        Returns:
            list[str]: A list of paths to the loaded frames.
        """
        available_extensions = (".jpg", ".jpeg", ".png")
        frame_paths = self.get_files_with_specific_extension_from_folder(frames_folder,
                                                                         frames_extension,
                                                                         available_extensions)
        logger.info("Frames loaded.")
        logger.debug("frame_paths: '%s'.", frame_paths)
        return frame_paths

    def score_all_frames(self, frame_paths: list[str]) -> list[tuple[np.ndarray, float]]:
        """Score each frame based on a defined criteria.

        Args:
            frame_paths (list[str]): A list of paths to the frames to be scored.

        Returns:
            list[tuple[np.ndarray, float]]: A list of tuples,
                each containing a frame (as ndarray) and its score.
        """
        scored_frames = []
        for frame_path in frame_paths:
            bgr_frame = cv2.imread(frame_path)
            frame_score = self._score_frame(bgr_frame)
            scored_frames.append((bgr_frame, frame_score))
            logger.debug("Frame '%s' scored. Score: %s", frame_path, frame_score)
        logger.info("Frames scored.")
        return scored_frames

    def save_top_frames(self, scored_frames: list[tuple[np.ndarray, float]],
                        threshold_percentile: int = 90) -> None:
        """Save the top frames based on their scores,
        determined by a specified percentile threshold.

        Args:
            scored_frames (list[tuple[np.ndarray, float]]): A list of tuples,
                each containing a frame and its score.
            threshold_percentile (int): The percentile value to determine
                the threshold for top frames. Defaults to 90.
        """
        scores = [score for _, score in scored_frames]
        threshold = np.percentile(scores, threshold_percentile)
        scored_frames.sort(key=lambda x: x[1], reverse=True)
        for frame, score in scored_frames:
            if score > threshold:
                self.save_ndarray_frame(self.output_folder, frame)
        logger.info("All top frames saved.")
