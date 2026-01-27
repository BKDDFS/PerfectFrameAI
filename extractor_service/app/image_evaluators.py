"""Provide abstract class for creating image evaluators and implementations.

Image evaluators:
    - InceptionResNetNIMA: NIMA model with helper classes.

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
from pathlib import Path

import numpy as np
import onnxruntime as ort
import requests

from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ImageEvaluator(ABC):
    """Abstract class for creating image evaluators."""

    @abstractmethod
    def __init__(self, config: ExtractorConfig) -> None:
        """Initialize the image evaluator with the provided configuration.

        Args:
            config (ExtractorConfig): Configuration from user.
        """

    @abstractmethod
    def evaluate_images(self, images: np.ndarray) -> list[float]:
        """Evaluate images batch and return scores.

        Args:
            images (list[np.ndarray]): Batch of images that will be evaluated.

        Returns:
            list[float]: List of images' scores.
        """

    @staticmethod
    def _check_scores(images: list[np.ndarray], scores: list[float]) -> None:
        """Check if the lengths of the images and scores lists match.

        Args:
            images (list[np.ndarray]): List of images.
            scores (list[float]): List of scores.
        """
        images_list_length = len(images)
        scores_list_length = len(scores)
        logger.debug("Scores: %s", scores)
        if images_list_length == scores_list_length:
            logger.debug("Scores and images lists length: %s", images_list_length)
        else:
            logger.warning("Scores and images lists lengths don't match!")
            logger.debug("Images list length: %s", images_list_length)
            logger.debug("Scores list length: %s", scores_list_length)


class InceptionResNetNIMA(ImageEvaluator):
    """NeuralImageAssessment model based image evaluator.

    It uses NIMA for evaluating aesthetics of images.
    """

    def __init__(self, config: ExtractorConfig) -> None:
        """Initialize the Neural Image Assessment with the provided configuration.

        Args:
            config (ExtractorConfig): Configuration object for the image evaluator.
        """
        model_path = _ONNXModel.get_model_path(config)
        self._session = ort.InferenceSession(str(model_path))
        self._input_name = self._session.get_inputs()[0].name

    def evaluate_images(self, images: np.ndarray) -> list[float]:
        """Evaluate a batch of images using the NIMA model, and return the results.

        Args:
            images (np.ndarray): Batch of numpy ndarray images to be evaluated.

        Returns:
            list[float]: List of scores corresponding to the input images.
        """
        logger.info("Evaluating images...")
        predictions = self._session.run(None, {self._input_name: images.astype(np.float32)})[0]
        weights = _ONNXModel.get_prediction_weights()
        scores = [self._calculate_weighted_mean(prediction, weights) for prediction in predictions]
        self._check_scores(images, scores)
        logger.info("Images batch evaluated.")
        return scores

    @staticmethod
    def _calculate_weighted_mean(prediction: np.array, weights: np.array = None) -> float:
        """Calculate the weighted mean of the prediction to get final image score.

        For example model InceptionResNetV2 returns 10 prediction scores for each image.
        We want to calculate weighted mean from that classification scores to calculate
        image final score. First classification score is less important and last is most.

        Args:
            prediction (np.array): Array of classification scores.
            weights (np.array): Optional weights for calculating weighted mean.
                If None, uses equal weights.

        Returns:
            float: Weighted mean of the prediction.
        """
        if weights is None:
            weights = np.ones_like(prediction)  # Default weights, equally distribute importance
        return np.sum(prediction * weights) / np.sum(weights)


class _ONNXModel:
    """Helper class for managing ONNX model weights.

    Handles downloading and caching of model weights.
    """

    class ModelWeightsDownloadError(Exception):
        """Error raised when there's an issue with downloading model weights."""

    _prediction_weights = np.arange(1, 11)

    @classmethod
    def get_prediction_weights(cls) -> np.ndarray:
        """Getter for prediction weights.

        Weights are for calculating weighted mean from model predictions.
        """
        return cls._prediction_weights

    @classmethod
    def get_model_path(cls, config: ExtractorConfig) -> Path:
        """Get the path to the ONNX model, downloading it if necessary.

        Args:
            config (ExtractorConfig): Configuration object for the model.

        Returns:
            Path: Path to the ONNX model file.
        """
        model_weights_directory = config.weights_directory
        logger.info(
            "Searching for model weights in weights directory: %s",
            model_weights_directory,
        )
        model_weights_path = Path(model_weights_directory) / config.weights_filename
        if not model_weights_path.is_file():
            logger.debug(
                "Can't find model weights in weights directory: %s",
                model_weights_directory,
            )
            cls._download_model_weights(model_weights_path, config)
        else:
            logger.debug("Model weights loaded from: %s", model_weights_path)
        return model_weights_path

    @classmethod
    def _download_model_weights(
        cls, weights_path: Path, config: ExtractorConfig, timeout: int = 10
    ) -> None:
        """Download the model weights from the specified URL.

        Args:
            weights_path (Path): Path to save the downloaded weights.
            config (ExtractorConfig): Configuration object with URL info.
            timeout (int): Timeout for the request in seconds.

        Raises:
            cls.ModelWeightsDownloadError: If there's an issue downloading the weights.
        """
        url = f"{config.weights_repo_url}{config.weights_filename}"
        logger.debug("Downloading model weights from ulr: %s", url)
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        if response.ok:
            weights_path.parent.mkdir(parents=True, exist_ok=True)
            weights_path.write_bytes(response.content)
            logger.debug("Model weights downloaded and saved to %s", weights_path)
        else:
            error_message = (
                f"Failed to download the weights: HTTP status code {response.status_code}"
            )
            logger.error(error_message)
            raise cls.ModelWeightsDownloadError(error_message)
