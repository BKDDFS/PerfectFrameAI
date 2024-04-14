"""Abstraction layer"""
import logging
import uuid
from abc import ABC
from pathlib import Path
from contextlib import contextmanager

import cv2
import pyiqa
import torch
import numpy as np
from torchvision import transforms

logger = logging.getLogger(__name__)


class ImageRater:
    metric_model = pyiqa.create_metric(model_name, device=torch_device)


class PyIQA:
    @staticmethod
    def rate_image(model: pyiqa.InferenceModel, image: torch.Tensor) -> float:
        rating = model(image).item()
        logger.debug("Image rated. Rating: %s", rating)
        return rating

    @staticmethod
    def get_torch_device() -> torch.device:
        """Get a torch device, CUDA if available, otherwise CPU.

        Returns:
            torch.device: The torch device object, either 'cuda' or 'cpu'.
        """
        if torch.cuda.is_available():
            logger.debug("Using CUDA for processing.")
            return torch.device('cuda')
        logger.warning("CUDA is unavailable!!! Using CPU for processing.")
        return torch.device('cpu')

    @staticmethod
    def convert_frame_rgb_to_tensor(rgb_frame: np.ndarray, transforms_compose: transforms.Compose,
                                    device: torch.device) -> torch.Tensor:
        tensor_frame = transforms_compose(rgb_frame).unsqueeze(0).to(device)
        logger.debug("Frame converted from RGB to TENSOR.")
        return tensor_frame

class CantOpenVideoCapture(Exception):
    pass


class VideoCaptureClosed(Exception):
    pass


class OpenCV:
    @staticmethod
    @contextmanager
    def video_capture(video_path: str) -> cv2.VideoCapture:
        video_cap = cv2.VideoCapture(video_path)
        try:
            if not video_cap.isOpened():
                error_massage = f"Can't open video file: {video_path}"
                logger.error(error_massage)
                raise CantOpenVideoCapture(error_massage)
            yield video_cap
        finally:
            video_cap.release()

    @classmethod
    def get_video_frames_pack(cls, video_cap: cv2.VideoCapture, required_size: int) -> list[np.ndarray]:
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
        fps = cls.get_video_frame_rate(video_cap)
        frame_count = 0
        frames_pack = []
        while True:
            if not video_cap.isOpened():
                error_massage = "Video capture was shut down before getting frames has been finished."
                logger.error(error_massage)
                raise VideoCaptureClosed(error_massage)
            read_result, bgr_frame = video_cap.read()
            if not read_result:
                yield frames_pack
                break
            frame_count += 1
            if frame_count % fps != 0: # get frame every 1 second
                continue
            frames_pack.append(bgr_frame)
            if len(frames_pack) == required_size:
                yield frames_pack
                frames_pack = []

    @staticmethod
    def get_video_frame_rate(video_cap: cv2.VideoCapture) -> int:
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

    @staticmethod
    def convert_image_to_rgb(bgr_frame: np.ndarray) -> np.ndarray:
        """Converts an image frame from BGR to RGB format.

        Args:
            bgr_frame (np.ndarray): The image frame in BGR format.

        Returns:
            np.ndarray: The converted image frame in RGB format.

        """
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        logger.debug("Frame converted from BGR to RGB.")
        return rgb_frame

    @staticmethod
    def save_image(image: np.ndarray, output_directory: Path,
                   output_filename: str, output_format: str = "jpg") -> Path:
        """Saves a ndarray image frame to a file in the specified format.

        Args:
            image (np.ndarray): The image frame in ndarray format to be saved.
            output_directory (str): The folder path where the image frame will be saved.
            output_filename (str):
            output_format (str): The format of the output file. Defaults to "jpg".

        Returns:
            str: The file path of the saved image frame.

        """
        image_path = output_directory / output_filename
        cv2.imwrite(str(image_path), image)
        logger.debug("Image saved at '%s'.", image_path)
        return image_path

class VideoManipulator:
    @staticmethod
    def get_next_video_frames(video_path: Path, quantity: int) -> :
        with OpenCV.video_capture(str(video_path)) as video_cap:
            for frames_pack in OpenCV.get_video_frames_pack(video_cap, quantity):
                yield frames_pack
