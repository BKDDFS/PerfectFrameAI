"""Provide abstract class for creating video processors and video processors.

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
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import cv2

from perfectframe.schemas import Image, Images

logger = logging.getLogger(__name__)


class VideoProcessor(ABC):
    """Abstract class for creating video processors used for managing video operations."""

    class _Error(Exception):
        """Video processor error."""

    @classmethod
    @abstractmethod
    def get_next_frames(cls, video_path: Path, frames_batch_size: int) -> Generator[Images]:
        """Abstract generator method to generate batches of frames from a video file."""


class OpenCVVideo(VideoProcessor):
    """Video processor based on OpenCV with FFMPEG extension."""

    @staticmethod
    @contextmanager
    def _video_capture(video_path: Path) -> Generator[cv2.VideoCapture]:
        """Get and release a video capture object."""
        video_cap = cv2.VideoCapture(str(video_path))
        try:
            if not video_cap.isOpened():
                error_message = f"Can't open video file: {video_path}"
                logger.error(error_message)
                raise OpenCVVideo._Error(error_message)
            logger.debug("Creating video capture.")
            yield video_cap
        finally:
            video_cap.release()

    @classmethod
    def get_next_frames(cls, video_path: Path, frames_batch_size: int) -> Generator[Images]:
        """Generate batches of frames from the specified video using OpenCV."""
        with cls._video_capture(video_path) as video:
            frame_rate = cls._get_video_property(video, cv2.CAP_PROP_FPS, "frame rate")
            total_frames = cls._get_video_property(video, cv2.CAP_PROP_FRAME_COUNT, "total frames")
            frames_batch: Images = []
            logger.info("Getting frames batch...")
            for frame_index in range(0, total_frames, frame_rate):
                frame = cls._read_next_frame(video, frame_index)
                if frame is None:
                    continue
                frames_batch.append(frame)
                logger.debug("Frame appended to frames batch.")
                if len(frames_batch) == frames_batch_size:
                    logger.info("Got full frames batch.")
                    yield frames_batch
                    frames_batch = []
            if frames_batch:
                logger.info("Returning last frames batch.")
                yield frames_batch

    @classmethod
    def _read_next_frame(cls, video: cv2.VideoCapture, frame_index: int) -> Image | None:
        """Read frame with specified index from provided video."""
        cls._check_video_capture(video)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = video.read()
        if not success:
            logger.warning("Couldn't read frame with index: %s", frame_index)
            return None
        return frame

    @classmethod
    def _get_video_property(
        cls, video: cv2.VideoCapture, property_id: int, property_name: str
    ) -> int:
        """Retrieve a specified property value from the video capture object and validate it."""
        cls._check_video_capture(video)
        property_value = video.get(property_id)
        logger.debug("Got input video %s: %s", property_name, property_value)
        if property_value <= 0:
            error_message = f"Invalid {property_name} retrieved: {property_value}."
            logger.error(error_message)
            raise ValueError(error_message)
        return round(property_value)

    @staticmethod
    def _check_video_capture(video: cv2.VideoCapture) -> None:
        """Check if video capture object is still available for future operations."""
        if not video.isOpened():
            error_message = (
                "Invalid video capture object or object not opened. "
                "Probably video capture closed at some point."
            )
            logger.error(error_message)
            raise ValueError(error_message)
