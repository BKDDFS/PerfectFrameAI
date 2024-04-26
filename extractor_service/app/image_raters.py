"""Abstraction layer"""
import logging
from abc import ABC, abstractmethod

import pyiqa
import torch
from torchvision import transforms
import numpy as np

logger = logging.getLogger(__name__)


class ImageRater(ABC):
    @abstractmethod
    def rate_images(self, images: list[np.ndarray]) -> list[float]:
        pass


class PyIQA(ImageRater):
    def __init__(self, metric_model: str = "nima") -> None:
        self.torch_device = self._get_torch_device()
        self.iqa_metric = pyiqa.create_metric(metric_model, device=self.torch_device).to(self.torch_device)
        self.transforms_compose = transforms.Compose([transforms.ToTensor()])

    def rate_images(self, images: list[np.ndarray]) -> list[float]:
        logger.info("Rating images...")
        tensor_batch = self._convert_images_to_tensor_batch(images)
        ratings = self.iqa_metric(tensor_batch).tolist()
        logger.info("Images batch rated.")
        return ratings

    @staticmethod
    def _get_torch_device() -> torch.device:
        """Get a torch device, CUDA if available, otherwise CPU.

        Returns:
            torch.device: The torch device object, either 'cuda' or 'cpu'.
        """
        if torch.cuda.is_available():
            logger.info("Using CUDA for processing.")
            return torch.device("cuda")
        logger.warning("CUDA is unavailable!!! Using CPU for processing.")
        return torch.device("cpu")

    def _convert_images_to_tensor_batch(self, images: list[np.ndarray]) -> torch.Tensor:
        tensor_images_list = [self.transforms_compose(image).to(self.torch_device) for image in images]
        tensor_images = torch.stack(tensor_images_list)
        logger.debug("Images batch converted to tensor.")
        return tensor_images
