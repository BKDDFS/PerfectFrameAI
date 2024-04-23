import logging
from abc import ABC, abstractmethod
from typing import Generator
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor(ABC):
    @classmethod
    @abstractmethod
    def get_next_video_frames(cls, video_path: Path,
                              quantity: int) -> Generator[list[np.ndarray], None, None]:
        pass


class OpenCVVideo(VideoProcessor):
    class CantOpenVideoCapture(Exception):
        """Exception raised when the video file cannot be opened."""
        pass

    class VideoCaptureClosed(Exception):
        """Exception raised when the video capture is prematurely closed."""
        pass

    @classmethod
    def get_next_video_frames(cls, video_path: Path, max_batch_size: int) -> Generator[list[np.ndarray], None, None]:
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
                if len(frames_batch) == max_batch_size:
                    logger.info("Got full frames batch.")
                    yield frames_batch
                    frames_batch = []
            if frames_batch:
                logger.info("Returning last frames batch.")
                yield frames_batch

    @staticmethod
    @contextmanager
    def _video_capture(video_path: str) -> cv2.VideoCapture:
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
