"""
This module provides abstract class for creating video processors and video processors.
Video processors:
    - OpenCVVideo: using OpenCV library to manage operations on videos.
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
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor(ABC):
    """Abstract class for creating video processors used for managing video operations."""
    @classmethod
    @abstractmethod
    def get_next_frames(cls, video_path: Path,
                        batch_size: int) -> Generator[list[np.ndarray], None, None]:
        """
        Abstract generator method to generate batches of frames from a video file.

        Args:
            video_path (Path): Path for video from which frames will be read.
            batch_size (int): Number of frames to include in each batch.

        Returns:
             Generator: Generator yielding batches of frames as lists of numpy ndarrays.

        Yields:
            list[np.ndarray]: A batch of video frames.
        """


class OpenCVVideo(VideoProcessor):
    """Video processor based on OpenCV with FFMPEG extension."""
    class CantOpenVideoCapture(Exception):
        """Exception raised when the video file cannot be opened."""

    class VideoCaptureClosed(Exception):
        """Exception raised when the video capture is prematurely closed."""

    @staticmethod
    @contextmanager
    def _video_capture(video_path: Path) -> cv2.VideoCapture:
        """
        Get and release a video capture object.

        Args:
            video_path (str): Path to the video file to be opened.

        Yields:
            cv2.VideoCapture: OpenCV video capture object.

        Raises:
            CantOpenVideoCapture: If the video file cannot be opened.
        """
        video_cap = cv2.VideoCapture(str(video_path))
        try:
            if not video_cap.isOpened():
                error_massage = f"Can't open video file: {video_path}"
                logger.error(error_massage)
                raise OpenCVVideo.CantOpenVideoCapture(error_massage)
            logger.debug("Creating video capture.")
            yield video_cap
        finally:
            video_cap.release()

    @classmethod
    def get_next_frames(cls, video_path: Path,
                        batch_size: int) -> Generator[list[np.ndarray], None, None]:
        """
        Generates batches of frames from the specified video using OpenCV.

        Args:
            video_path (Path): Path for video from which frames will be read.
            batch_size (int): Maximum number of frames per batch.

        Returns:
            Generator: Generator yielding batches of frames as lists of numpy ndarrays.

        Yields:
            list[np.ndarray]: A batch of video frames.
        """
        with cls._video_capture(video_path) as video:
            frame_rate = cls._get_video_attribute(
                video, cv2.CAP_PROP_FPS, "frame rate")
            total_frames = cls._get_video_attribute(
                video, cv2.CAP_PROP_FRAME_COUNT, "total frames")
            frames_batch = []
            logger.info("Getting frames batch...")
            for frame_index in range(0, total_frames, frame_rate):
                frame = cls._read_next_frame(video, frame_index)
                frames_batch.append(frame)
                logger.debug("Frame appended to frames batch.")
                if len(frames_batch) == batch_size:
                    logger.info("Got full frames batch.")
                    yield frames_batch
                    frames_batch = []
            if frames_batch:
                logger.info("Returning last frames batch.")
                yield frames_batch

    @classmethod
    def _read_next_frame(cls, video: cv2.VideoCapture, frame_index: int) -> np.ndarray | None:
        """
        Reads frame with specified index from provided video.

        Args:
            video: Video capture object from which frame will be taken.
            frame_index (int): Place of the frame in video among other frames measured in indexes.

        Returns:
            np.ndarray: Decoded frame.
        """
        cls._check_video_capture(video)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = video.read()
        if not success:
            logger.warning("Couldn't read frame with index: %s", frame_index)
            return None
        return frame

    @classmethod
    def _get_video_attribute(cls, video: cv2.VideoCapture,
                             attribute_id: int, display_name: str) -> int:
        """
        Retrieves a specified attribute value from the video capture object and validates it.

        Args:
            attribute_id (int): OpenCV video capture ID of the attribute to retrieve.
            display_name (str): Descriptive name of the attribute for logging purposes.

        Returns:
            int: The value of the requested attribute, validated to be a positive integer.

        Raises:
            ValueError: If the retrieved value is invalid.
        """
        cls._check_video_capture(video)
        attribute_value = video.get(attribute_id)
        logger.debug("Got input video %s: %s", display_name, attribute_value)
        if attribute_value <= 0:
            error_message = f"Invalid {display_name} retrieved: {attribute_value}."
            logger.error(error_message)
            raise ValueError(error_message)
        attribute = int(round(attribute_value))
        return attribute

    @staticmethod
    def _check_video_capture(video: cv2.VideoCapture) -> None:
        """
        Checks is video capture object still available for future operations.

        Args:
            video (cv2.VideoCapture): Video capture object that will be checked.

        Raises:
            ValueError: If the video capture object is not opened.
        """
        if not video.isOpened():
            error_message = ("Invalid video capture object or object not opened. "
                             "Probably video capture closed at some point.")
            logger.error(error_message)
            raise ValueError(error_message)
