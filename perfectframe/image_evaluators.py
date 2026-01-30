"""Provide abstract class for creating image evaluators and implementations.

Image evaluators:
    - NIMAEvaluator: NIMA-based image evaluator using ONNX runtime.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import onnxruntime as ort
import requests

from perfectframe.schemas import (
    ExtractorConfig,
    ImagesBatch,
    NIMAModelOutput,
    Score,
    Scores,
)

logger = logging.getLogger(__name__)


class ImageEvaluator(ABC):
    """Abstract class for creating image evaluators."""

    @abstractmethod
    def __init__(self, config: ExtractorConfig) -> None:
        """Initialize the image evaluator with the provided configuration."""

    @abstractmethod
    def evaluate_images(self, images: ImagesBatch) -> Scores:
        """Evaluate images batch and return scores."""

    @staticmethod
    def _check_scores(images: ImagesBatch, scores: Scores) -> None:
        """Check if the lengths of the images and scores lists match."""
        images_list_length = len(images)
        scores_list_length = len(scores)
        logger.debug("Scores: %s", scores)
        if images_list_length == scores_list_length:
            logger.debug("Scores and images lists length: %s", images_list_length)
        else:
            logger.warning("Scores and images lists lengths don't match!")
            logger.debug("Images list length: %s", images_list_length)
            logger.debug("Scores list length: %s", scores_list_length)


class NIMAEvaluator(ImageEvaluator):
    """NIMA-based image evaluator using ONNX runtime."""

    class ModelWeightsDownloadError(Exception):
        """Error raised when there's an issue with downloading model weights."""

    _prediction_weights = np.arange(1, 11)

    def __init__(self, config: ExtractorConfig) -> None:
        """Initialize the NIMA evaluator with the provided configuration."""
        model_path = self._get_model_path(config)
        self._session = ort.InferenceSession(str(model_path))
        self._input_name = self._session.get_inputs()[0].name

    def evaluate_images(self, images: ImagesBatch) -> Scores:
        """Evaluate a batch of images using the NIMA model."""
        logger.info("Evaluating images...")
        predictions = self._session.run(None, {self._input_name: images.astype(np.float32)})[0]
        if not isinstance(predictions, np.ndarray):
            return []
        scores = [self._calculate_weighted_mean(p) for p in predictions]
        self._check_scores(images, scores)
        logger.info("Images batch evaluated.")
        return scores

    def _calculate_weighted_mean(self, prediction: NIMAModelOutput) -> Score:
        """Calculate the weighted mean of the prediction to get final image score.

        For example model InceptionResNetV2 returns 10 prediction scores for each image. We want to
        calculate weighted mean from that classification scores to calculate image final score.
        First classification score is less important and last is most.
        """
        return np.sum(prediction * self._prediction_weights) / np.sum(self._prediction_weights)

    @classmethod
    def _get_model_path(cls, config: ExtractorConfig) -> Path:
        """Get the path to the ONNX model, downloading it if necessary."""
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
        """Download the model weights from the specified URL."""
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
