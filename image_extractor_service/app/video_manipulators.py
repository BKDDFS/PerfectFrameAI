import logging
from abc import ABC, abstractmethod
from typing import Generator
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoManipulator(ABC):
    @classmethod
    @abstractmethod
    def get_next_video_frames(cls, video_path: Path, quantity: int) -> Generator[list[np.ndarray]]:
        pass


class OpenCVVideo(VideoManipulator):
    class CantOpenVideoCapture(Exception):
        """Exception raised when the video file cannot be opened."""
        pass

    class VideoCaptureClosed(Exception):
        """Exception raised when the video capture is prematurely closed."""
        pass

    @classmethod
    def get_next_video_frames(cls, video_path: Path, quantity: int) -> list[np.ndarray]:
        with cls._video_capture(str(video_path)) as video_cap:
            for frames_pack in cls._get_video_frames_pack(video_cap, quantity):
                yield frames_pack

    @staticmethod
    @contextmanager
    def _video_capture(video_path: str) -> cv2.VideoCapture:
        video_cap = cv2.VideoCapture(video_path)
        try:
            if not video_cap.isOpened():
                error_massage = f"Can't open video file: {video_path}"
                logger.error(error_massage)
                raise OpenCVVideo.CantOpenVideoCapture(error_massage)
            yield video_cap
        finally:
            video_cap.release()

    @classmethod
    def _get_video_frames_pack(cls, video_cap: cv2.VideoCapture, required_size: int) -> Generator[list[np.ndarray]]:
        """Process video frames to extract and save the best frame.

        Reads every frame sequentially to handle inter-frame
         dependencies in compressed video formats (like H.264).
        This ensures complete and accurate information for each frame,
         especially important when extracting frames
        at one-second intervals based on the video's FPS.

        Args:
            video_cap (cv2.VideoCapture): VideoCapture object for the video.
            frames_to_compare (int): Number of
                frames to compare to extract the best one.
                :param required_size:
                :param video_cap:
                :param frames_pack_size:
        """
        fps = cls._get_video_frame_rate(video_cap)
        frame_count = 0
        frames_pack = []
        while True:
            if not video_cap.isOpened():
                error_massage = "Video capture was shut down before getting frames has been finished."
                logger.error(error_massage)
                raise OpenCVVideo.VideoCaptureClosed(error_massage)
            read_result, bgr_frame = video_cap.read()
            if not read_result:
                yield frames_pack
                break
            frame_count += 1
            if frame_count % fps != 0:  # get frame every 1 second
                continue
            frames_pack.append(bgr_frame)
            if len(frames_pack) == required_size:
                yield frames_pack
                frames_pack = []

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
        logger.debug("Input video frame rate: %s", video_frame_rate)
        video_frame_rate = int(round(video_frame_rate))
        return video_frame_rate

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
