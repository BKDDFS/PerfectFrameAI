"""Abstraction layer"""
import logging
from abc import ABC, abstractmethod

import pyiqa
import torch
from torchvision import transforms
import numpy as np

logger = logging.getLogger(__name__)


class ImageRater(ABC):
    @classmethod
    @abstractmethod
    def rate_images(cls, images: list[np.ndarray], model_name: str) -> list[float]:
        pass


class PyIQA:
    @classmethod
    def rate_images(cls, images: list[np.ndarray], model_name: str = "nima") -> list[float]:
        torch_device = cls._get_torch_device()
        iqa_metric = pyiqa.create_metric(model_name, device=torch_device).to(torch_device)
        transforms_compose = transforms.Compose([transforms.ToTensor()])
        tensor_batch = cls._convert_images_to_tensor_batch(images, transforms_compose, torch_device)
        ratings = iqa_metric(tensor_batch, color_space="bgr").to_list()
        return ratings

    @staticmethod
    def _get_torch_device() -> torch.device:
        """Get a torch device, CUDA if available, otherwise CPU.

        Returns:
            torch.device: The torch device object, either 'cuda' or 'cpu'.
        """
        if torch.cuda.is_available():
            logger.debug("Using CUDA for processing.")
            return torch.device("cuda")
        logger.warning("CUDA is unavailable!!! Using CPU for processing.")
        return torch.device("cpu")

    @staticmethod
    def _convert_images_to_tensor_batch(images: list[np.ndarray], transforms_compose: transforms.Compose,
                                        device: torch.device) -> torch.Tensor:
        tensor_images = torch.stack([transforms_compose(image).to(device) for image in images])
        logger.debug("Batch of images converted from RGB to TENSOR.")
        return tensor_images
