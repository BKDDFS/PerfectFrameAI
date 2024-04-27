"""
This module provides abstract class for creating video processors and video processors.
Video processors:
    - OpenCVVideo: using OpenCV library to manage operations on videos.
"""
import logging
from abc import ABC, abstractmethod
from typing import Generator
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor(ABC):
    """Abstract class for creating video processors used for managing video operations."""
    @classmethod
    @abstractmethod
    def get_next_video_frames(cls, video_path: Path,
                              batch_size: int) -> Generator[list[np.ndarray], None, None]:
        """
        Abstract generator method to generate batches of frames from a video file.

        Args:
            video_path (Path): Path to the video file from which frames will be extracted.
            batch_size (int): Number of frames to include in each batch.

        Returns:
             Generator: Generator yielding batches of frames as lists of numpy ndarrays.

        Yields:
            list[np.ndarray]: A batch of video frames.
        """


class OpenCVVideo(VideoProcessor):
    class CantOpenVideoCapture(Exception):
        """Exception raised when the video file cannot be opened."""
        pass

    class VideoCaptureClosed(Exception):
        """Exception raised when the video capture is prematurely closed."""
        pass

    @classmethod
    def get_next_video_frames(cls, video_path: Path,
                              batch_size: int) -> Generator[list[np.ndarray], None, None]:
        """
        Generates batches of frames from the specified video using OpenCV.

        Args:
            video_path (Path): Path to the video file.
            batch_size (int): Maximum number of frames per batch.

        Returns:
            Generator: Generator yielding batches of frames as lists of numpy ndarrays.

        Yields:
            list[np.ndarray]: A batch of video frames.
        """
        with cls._video_capture(str(video_path)) as video_cap:
            fps = cls._get_video_frame_rate(video_cap)
            total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames_batch = []
            logger.info("Getting frames batch...")
            for i in range(0, total_frames, fps):
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                success, frame = video_cap.read()
                if not success:
                    break
                frames_batch.append(frame)
                logger.debug("Frame appended to frames batch.")
                if len(frames_batch) == batch_size:
                    logger.info("Got full frames batch.")
                    yield frames_batch
                    frames_batch = []
            if frames_batch:
                logger.info("Returning last frames batch.")
                yield frames_batch

    @staticmethod
    @contextmanager
    def _video_capture(video_path: str) -> cv2.VideoCapture:
        """
        Context manager for safely creating and releasing a video capture object.

        Args:
            video_path (str): Path to the video file to be opened.

        Yields:
            cv2.VideoCapture: OpenCV video capture object.

        Raises:
            CantOpenVideoCapture: If the video file cannot be opened.
        """
        video_cap = cv2.VideoCapture(video_path)
        try:
            if not video_cap.isOpened():
                error_massage = f"Can't open video file: {video_path}"
                logger.error(error_massage)
                raise OpenCVVideo.CantOpenVideoCapture(error_massage)
            logger.debug("Creating video capture.")
            yield video_cap
        finally:
            video_cap.release()

    @staticmethod
    def _get_video_frame_rate(video_cap: cv2.VideoCapture) -> int:
        """
        Retrieves the frame rate of the video being captured.

        Args:
            video_cap (cv2.VideoCapture): The video capture object from which
                the frame rate will be retrieved.

        Returns:
            int: The frame rate of the video.

        Raises:
            ValueError: If the video capture object is invalid or the frame rate is non-positive.
        """
        if not video_cap.isOpened():
            error_massage = "Provided invalid video_cap."
            logger.error(error_massage)
            raise ValueError(error_massage)
        video_frame_rate = video_cap.get(cv2.CAP_PROP_FPS)
        if video_frame_rate <= 0:
            error_massage = f"Invalid frame rate retrieved: {video_frame_rate}"
            logger.error(error_massage)
            raise ValueError(error_massage)
        logger.info("Got input video frame rate: %s", video_frame_rate)
        video_frame_rate = int(round(video_frame_rate))
        return video_frame_rate
