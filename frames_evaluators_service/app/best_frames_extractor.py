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
import os
import logging
from typing import Generator

import cv2
import numpy as np

from .evaluator import Evaluator

logger = logging.getLogger(__name__)


class BestFramesExtractor(Evaluator):
    """A class derived from Evaluator that extracts the best frames from video files.

    This class scans a specified folder for video files and processes each video to
    extract and save the best frames based on a scoring mechanism defined in the Evaluator
    class. It filters video files based on their format and whether they have already
    been processed.

    Attributes:
        None specific to this class. Inherits attributes from the Evaluator class.

    Methods:
        process(videos_folder): Processes all videos in the specified folder.
        extract_best_frames_from_all_videos_in_folder(...): Extracts
        best frames from all videos in the folder.
        filter_video_files(...): Filters video files in the folder.
        extract_best_frames_from_video(...): Extracts and saves the best frames from a single video.
        process_video_frames(...): Processes video frames to extract the best frame.
        extract_and_save_best_frame(...): Extracts and saves the best frame from a batch of frames.
        change_processed_video_name(...): Renames a processed video file.
        get_video_capture(...): Opens a video file and returns a cv2.VideoCapture object.
    """

    def process(self, input_folder: str) -> None:
        """Process all videos in the given folder to extract best frames.

        Args:
            input_folder (str): Path to the folder containing video files.
        """
        logger.info("Starting frames extraction process from '%s'...", input_folder)
        self.extract_best_frames_from_all_videos_in_folder(input_folder)

    def extract_best_frames_from_all_videos_in_folder(self, videos_folder: str,
                                                      videos_extension: str = ".mp4",
                                                      number_of_frames_to_compare: int = 5,
                                                      done_video_prefix: str = "frames_extracted_"
                                                      ) -> None:
        """Extract best frames from all videos in the given folder.

        Args:
            videos_folder (str): Path to the folder containing video files.
            videos_extension (str): Video file format to process (default is .mp4).
            number_of_frames_to_compare (int): Number of frames to
            compare to find the best one.
            done_video_prefix (str): Prefix added to the video
            filenames once processed.
        """
        for video_path, video_filename in self.filter_videos_from_files(videos_folder,
                                                                        videos_extension,
                                                                        done_video_prefix):
            self.extract_best_frames_from_video(video_path, number_of_frames_to_compare)
            self.change_processed_video_name(videos_folder, video_path,
                                             video_filename, done_video_prefix)

    def filter_videos_from_files(self, videos_folder: str,
                                 videos_extension: str,
                                 done_video_prefix: str
                                 ) -> Generator[tuple[str, str], None, None]:
        """Filter out video files that are already processed or not in the desired format.

        Args:
            videos_folder (str): Path to the folder containing video files.
            videos_extension (str): Video file format to look for.
            done_video_prefix (str): Prefix to identify already processed files.

        Returns:
            Generator[str, None, None]: A generator yielding video file names.
        """
        available_extensions = (".avi", ".mp4", ".mov", ".webm", ".wmv", ".flv")
        video_paths = self.get_files_with_specific_extension_from_folder(videos_folder,
                                                                         videos_extension,
                                                                         available_extensions)
        for video_path in video_paths:
            video_filename = os.path.basename(video_path)
            if not video_filename.startswith(done_video_prefix):
                logger.debug("Valid video found. Video: '%s'.", video_filename)
                yield video_path, video_filename

    def extract_best_frames_from_video(self, video_path: str,
                                       number_of_frames_to_compare: int = 10) -> None:
        """Extract and save the best frames from the given video.

        Args:
            video_path (str): Path to the video file.
            number_of_frames_to_compare (int): Number of frames to compare to extract the best one.
        """
        if number_of_frames_to_compare < 2:
            raise ValueError(f"number_of_frames_to_compare must be bigger than 2. "
                             f"You provided: {number_of_frames_to_compare}.")
        logger.info("Extracting best frames from video '%s'...", video_path)
        cap = self.get_video_capture(video_path)
        try:
            self.process_video_frames(cap, number_of_frames_to_compare)
        finally:
            cap.release()

    def process_video_frames(self, cap: cv2.VideoCapture,
                             number_of_frames_to_compare: int) -> None:
        """Process video frames to extract and save the best frame.

        Reads every frame sequentially to handle inter-frame
         dependencies in compressed video formats (like H.264).
        This ensures complete and accurate information for each frame,
         especially important when extracting frames
        at one-second intervals based on the video's FPS.

        Args:
            cap (cv2.VideoCapture): VideoCapture object for the video.
            number_of_frames_to_compare (int): Number of
                frames to compare to extract the best one.
        """
        frames_per_second = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        batch_frames = []
        while cap.isOpened():
            read_result, bgr_frame = cap.read()
            if not read_result:
                break
            frame_count += 1
            if frame_count % int(frames_per_second) == 0:  # get frame every 1 second
                self._extract_and_save_best_frame(bgr_frame, batch_frames,
                                                  number_of_frames_to_compare)

    def _extract_and_save_best_frame(self, bgr_frame: np.ndarray,
                                     batch_frames: list[tuple[np.ndarray, float]],
                                     number_of_frames_to_compare: int) -> None:
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
        score = self._score_frame(bgr_frame)
        batch_frames.append((bgr_frame, score))
        if len(batch_frames) == number_of_frames_to_compare:
            best_frame, _ = max(batch_frames, key=lambda x: x[1])
            self.save_ndarray_frame(self.output_folder, best_frame)
            logger.debug("Frame '%s' saved.", best_frame)
            batch_frames.clear()

    @staticmethod
    def change_processed_video_name(videos_folder: str, video_path: str,
                                    video_filename: str, complete_videos_prefix: str) -> None:
        """Change the name of the processed video.

        Args:
            videos_folder (str): Path to the folder containing video files.
            video_path (str): Full path to the video file.
            video_filename (str): Filename of the video.
            complete_videos_prefix (str): Prefix to add to the processed video filename.
        """
        new_video_path = os.path.join(videos_folder, complete_videos_prefix + video_filename)
        os.rename(video_path, new_video_path)
        logger.debug("Video path '%s' changed to '%s'", video_path, new_video_path)

    @staticmethod
    def get_video_capture(video_path: str) -> cv2.VideoCapture:
        """Get a video capture object for the given path.

        Args:
            video_path (str): Path to the video file.

        Returns:
            cv2.VideoCapture: VideoCapture object for the video.

        Raises:
            ValueError: If the video file cannot be opened.
        """
        capture = cv2.VideoCapture(video_path)
        if not capture.isOpened():
            capture.release()
            raise ValueError(f"Can't open: {video_path}")
        return capture
