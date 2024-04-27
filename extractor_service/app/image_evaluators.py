"""
This module provides abstract class for creating image evaluators and image evaluators.
Image evaluators:
    - PyIQA: using PyIQA library and its model in Pytorch to evaluate images.
"""
import logging
from abc import ABC, abstractmethod

import pyiqa
import torch
from torchvision import transforms
import numpy as np

logger = logging.getLogger(__name__)


class ImageEvaluator(ABC):
    """Abstraction class for creating image evaluators."""
    @abstractmethod
    def evaluate_images(self, images: list[np.ndarray]) -> list[float]:
        """
        Evaluates images batch and returns it.

        Args:
            images (list[np.ndarray]): Batch of images that will be evaluated.

        Returns:
            list[float]: List of images' scores.
        """


class PyIQA(ImageEvaluator):
    """Implementation of image evaluator using PyIQA library."""
    def __init__(self, metric_model: str = "nima") -> None:
        """
        Initialize Pytorch device and transform_compose. Creating metric from model given model name.
        If metric model is not available in cache it will be downloaded.

        Args:
            metric_model (str): Name of metric model that will be used by PyIQA.
        """
        self.torch_device = self._get_torch_device()
        self.iqa_metric = pyiqa.create_metric(metric_model, device=self.torch_device).to(self.torch_device)
        self.transforms_compose = transforms.Compose([transforms.ToTensor()])

    def evaluate_images(self, images: list[np.ndarray]) -> list[float]:
        """
        Converts images to tensor batch. Scores images batch and returns it.

        Args:
            images (list[np.ndarray]): Batch of images that will be evaluated.

        Returns:
            list[float]: List of images' scores.
        """
        logger.info("Evaluating images...")
        tensor_batch = self._convert_images_to_tensor_batch(images)
        scores = self.iqa_metric(tensor_batch).tolist()
        logger.info("Images batch evaluated.")
        return scores

    @staticmethod
    def _get_torch_device() -> torch.device:
        """
        Get a torch device, CUDA if available, otherwise CPU.

        Returns:
            torch.device: The torch device object ('cuda' or 'cpu').
        """
        if torch.cuda.is_available():
            logger.info("Using CUDA for processing.")
            return torch.device("cuda")
        logger.warning("CUDA is unavailable!!! Using CPU for processing.")
        return torch.device("cpu")

    def _convert_images_to_tensor_batch(self, images: list[np.ndarray]) -> torch.Tensor:
        """
        Converts numpy ndarray images list to tensor batch.

        Args:
            images: Batch of images that will be converted.

        Returns:
            torch.Tensor: Images batch in tensor object.
        """
        tensor_images_list = [self.transforms_compose(image).to(self.torch_device) for image in images]
        tensor_images = torch.stack(tensor_images_list)
        logger.debug("Images batch converted to tensor.")
        return tensor_images
