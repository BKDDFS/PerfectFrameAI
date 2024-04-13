"""This module provides the Evaluator abstract class, designed for video and image
evaluation tasks using various image quality assessment (IQA) metrics.

The module integrates functionalities from libraries such as OpenCV, PyTorch, Numpy,
and PyIQA, offering tools to process and evaluate image and video data. It supports
operations like converting image formats, applying transformations, scoring frames, and
saving results.

Classes:
    Evaluator: An abstract base class for creating specific evaluators for image and
               video analysis tasks, leveraging different IQA metrics and processing
               techniques.
"""
import os
from abc import ABC, abstractmethod
import logging
import time
from glob import glob

import cv2
import torch
import numpy as np
import pyiqa
from torchvision import transforms

logger = logging.getLogger(__name__)


class Evaluator(ABC):
    """Abstract base class for image and video evaluation tasks using IQA metrics.

    This class provides a foundation for implementing evaluators with functionalities
    for scoring frames using specific image quality assessment models. It handles device
    selection (CPU or CUDA), initializing IQA models, and basic image processing
    operations.

    Attributes:
        device (torch.device): Device used for computations, either CPU or CUDA.
        output_folder (str): Path to the folder where results are saved.
        iqa_metric (pyiqa.InferenceModel): Inference model for image quality assessment.
        transforms_compose (transforms.Compose): Transformations to apply to images.

    Methods:
        process(*args): Abstract method to be implemented by subclasses for specific
                        video or image processing tasks.
        _score_frame(bgr_frame): Scores an image frame using the IQA model.
        convert_frame_bgr_to_rgb(bgr_frame): Converts a frame from BGR to RGB format.
        convert_frame_rgb_to_tensor(rgb_frame, transforms_compose, device): Converts
                               an RGB frame to a PyTorch tensor.
        save_ndarray_frame(output_folder, ndarray_frame, output_format): Saves an
                                    image frame to a file in a specified format.
    """
    def __init__(self, output_folder: str, metric_model: str = "nima",
                 transforms_compose: transforms.Compose = None,
                 iqa_metric: pyiqa.InferenceModel = None):
        """Initializes an Evaluator object with specified parameters.

        Args:
            output_folder: Path to the folder where results will be saved.
            metric_model: Name of the IQA metric model (default is "nima").
            transforms_compose: Compose object with image transformations.
            iqa_metric: InferenceModel object for image quality assessment.
        """
        self.device = self.get_torch_device()
        self._check_folder_exists(output_folder)
        self.output_folder = output_folder
        self.iqa_metric = iqa_metric if iqa_metric \
            else pyiqa.create_metric(metric_model, device=self.device)
        self.transforms_compose = transforms_compose if transforms_compose \
            else transforms.Compose([transforms.ToTensor()])

    @staticmethod
    def _check_folder_exists(folder_path: str) -> None:
        """Checks if the specified folder exists and creates it if not.

        Args:
            folder_path: Path to the folder to check or create.
        """
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    @abstractmethod
    def process(self, input_folder: str) -> None:
        """Abstract method to process video data.

        Args:
            input_folder: Arguments required for video processing.

        This method should be implemented by subclasses.
        """

    @staticmethod
    def get_torch_device() -> torch.device:
        """Get torch device, CUDA if available, otherwise CPU.

        Returns:
            torch.device: The torch device object, either 'cuda' or 'cpu'.
        """
        if torch.cuda.is_available():
            logger.debug("Using CUDA for processing.")
            return torch.device('cuda')
        logger.warning("CUDA is not available!!! Using CPU for processing.")
        return torch.device('cpu')

    def _score_frame(self, bgr_frame: np.ndarray) -> float:
        """Scores the quality of an image frame and returns the score.

        Args:
            bgr_frame (np.ndarray): The image frame in BGR format to be scored.

        Returns:
            float: The quality score of the frame.

        """
        rgb_frame = self.convert_frame_bgr_to_rgb(bgr_frame)
        tensor_format_frame = self.convert_frame_rgb_to_tensor(rgb_frame,
                                                               self.transforms_compose,
                                                               self.device)
        score = self.iqa_metric(tensor_format_frame).item()
        logger.debug("Frame scored. Score: %s", score)
        return score

    @staticmethod
    def convert_frame_bgr_to_rgb(bgr_frame: np.ndarray) -> np.ndarray:
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
    def convert_frame_rgb_to_tensor(rgb_frame: np.ndarray, transforms_compose: transforms.Compose,
                                    device: torch.device) -> torch.Tensor:
        """Converts an RGB image frame to a PyTorch tensor.

        Args:
            rgb_frame (np.ndarray): The image frame in RGB format.
            transforms_compose (transforms.Compose): Transformations to apply to the frame.
            device (torch.device): The torch device to which the tensor is moved.

        Returns:
            torch.Tensor: The image frame as a PyTorch tensor.

        """
        tensor_frame = transforms_compose(rgb_frame).unsqueeze(0).to(device)
        logger.debug("Frame converted from RGB to TENSOR.")
        return tensor_frame

    @staticmethod
    def save_ndarray_frame(output_folder: str,
                           ndarray_frame: np.ndarray,
                           output_format: str = "jpg") -> str:
        """Saves a ndarray image frame to a file in the specified format.

        Args:
            output_folder (str): The folder path where the image frame will be saved.
            ndarray_frame (np.ndarray): The image frame in ndarray format to be saved.
            output_format (str, optional): The format of the output file. Defaults to "jpg".

        Returns:
            str: The file path of the saved image frame.

        """
        timestamp = int(time.time() * 1000)  # milliseconds
        frame_name = f"best_frame_{timestamp}.{output_format}"
        frame_path = os.path.join(output_folder, frame_name)
        cv2.imwrite(frame_path, ndarray_frame)
        logger.debug("Frame saved at '%s'.", frame_path)
        return frame_path

    def get_files_with_specific_extension_from_folder(self, folder_path: str,
                                                      files_extension: str,
                                                      available_extensions: tuple[str, ...]
                                                      ) -> list[str]:
        """Retrieves file paths with a specific extension from a given folder.

        Args:
            folder_path (str): The path to the folder from which to retrieve files.
            files_extension (str): The file extension to filter the files.
            available_extensions (tuple[str, ...]): A tuple of valid file extensions.

        Returns:
            list[str]: A list of file paths matching the specified file extension.

        Raises:
            ValueError: If the folder path does not
                exist or the file extension is not valid.
        """
        self.check_extension_is_valid(files_extension, available_extensions)
        if not os.path.isdir(folder_path):
            raise ValueError(f"Can't find folder '{folder_path}'.")
        file_paths = glob(os.path.join(folder_path, f'*{files_extension}'))
        if not file_paths:
            logger.warning("Couldn't find any files with extension '%s' in folder '%s'.",
                           files_extension, folder_path)
        return file_paths

    @staticmethod
    def check_extension_is_valid(extension: str, available_extensions: tuple[str, ...]) -> bool:
        """Validates if the provided file extension is among the available extensions.

        Args:
            extension (str): The file extension to validate.
            available_extensions (tuple[str, ...]): A tuple of valid file extensions.

        Returns:
            bool: True if the extension is valid, False otherwise.

        Raises:
            ValueError: If the provided file extension is not in the list of available extensions.
        """
        if extension in available_extensions:
            return True
        raise ValueError(f"You provided invalid video extension: {extension}. "
                         f"Available extensions: {available_extensions}")
