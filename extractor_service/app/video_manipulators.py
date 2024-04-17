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
    def get_next_video_frames(cls, video_path: Path,
                              quantity: int) -> Generator[list[np.ndarray], None, None]:
        pass


# class FFmpegPythonVideo:
#     @staticmethod
#     def get_next_video_frames(video_path: Path, quantity: int, fps: int) -> Generator[np.ndarray, None, None]:
#         # Utwórz proces ffmpeg, który odczytuje klatki co określony interwał czasu (co sekundę)
#         out, _ = (
#             ffmpeg
#             .input(str(video_path), hwaccel='cuda', hwaccel_device=0, vsync='0')  # Ustawienia dla CUDA mogą wymagać odpowiedniej konfiguracji
#             .output('pipe:', format='rawvideo', pix_fmt='rgb24', r=fps)
#             .run(capture_stdout=True, capture_stderr=True)
#         )
#
#         # Przetwarzaj dane wyjściowe na klatki
#         video_width = int(ffmpeg.probe(str(video_path))['streams'][0]['width'])
#         video_height = int(ffmpeg.probe(str(video_path))['streams'][0]['height'])
#         frame_size = video_width * video_height * 3  # RGB ma 3 bajty na piksel
#
#         frames = []
#         for i in range(0, len(out), frame_size):
#             if len(frames) < quantity:
#                 frame = np.frombuffer(out[i:i+frame_size], np.uint8).reshape((video_height, video_width, 3))
#                 frames.append(frame)
#             if len(frames) == quantity:
#                 yield frames
#                 frames = []
#
#         if frames:
#             yield frames

class OpenCVVideo(VideoManipulator):
    class CantOpenVideoCapture(Exception):
        """Exception raised when the video file cannot be opened."""
        pass

    class VideoCaptureClosed(Exception):
        """Exception raised when the video capture is prematurely closed."""
        pass

    @classmethod
    def get_next_video_frames(cls, video_path: Path, quantity: int) -> Generator[list[np.ndarray], None, None]:
        with cls._video_capture(str(video_path)) as video_cap:
            fps = cls._get_video_frame_rate(video_cap)
            total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames = []
            # Przeskakuj po filmie co 'fps' klatek, czyli co sekundę.
            for i in range(0, total_frames, fps):
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                success, frame = video_cap.read()
                if not success:
                    break
                frames.append(frame)
                logger.debug("Frame appended to frames pack.")
                if len(frames) == quantity:
                    yield frames
                    frames = []  # Resetowanie listy frames po zwróceniu.
            if frames:
                yield frames  # Zwróć pozostałe klatki, jeśli ich liczba była mniejsza niż 'quantity'.

    # @classmethod
    # def get_next_video_frames(cls, video_path: Path,
    #                           quantity: int) -> Generator[list[np.ndarray], None, None]:
    #     with cls._video_capture(str(video_path)) as video_cap:
    #         fps = cls._get_video_frame_rate(video_cap)
    #         frame_count = 0
    #         frames = []
    #         while True:
    #             if not video_cap.isOpened():
    #                 error_massage = "Video capture was shut down before getting frames has been finished."
    #                 logger.error(error_massage)
    #                 raise OpenCVVideo.VideoCaptureClosed(error_massage)
    #             read_result, bgr_frame = video_cap.read()
    #             if not read_result:
    #                 yield frames
    #                 break
    #             frame_count += 1
    #             if frame_count % fps != 0:  # get frame every 1 second
    #                 continue
    #             frames.append(bgr_frame)
    #             logger.debug("Frame appended to frames pack.")
    #             if len(frames) == quantity:
    #                 yield frames
    #                 frames = []

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
