"""
This module provides abstract class for creating image evaluators and image evaluators.
Image evaluators:
    - NeuralImageAssessment: NIMA model based on the InceptionResNetV2 architecture.
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2

from .image_processors import OpenCVImage
from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ImageEvaluator(ABC):
    """Abstract class for creating image evaluators."""
    @abstractmethod
    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the image evaluator with the provided configuration.

        Args:
            config (ExtractorConfig): Configuration from user.
        """

    @abstractmethod
    def evaluate_images(self, images: list[np.ndarray]) -> list[float]:
        """
        Evaluates images batch and returns it.

        Args:
            images (list[np.ndarray]): Batch of images that will be evaluated.

        Returns:
            list[float]: List of images' scores.
        """

    @staticmethod
    def _check_scores(images: list[np.ndarray], scores: list[float]) -> None:
        """
        Check if the lengths of the images and scores lists match.

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
    """
    NeuralImageAssessment model based image evaluator.
    It uses NIMA for evaluating aesthetics of images.
    NIMA google research:
    https://research.google/blog/introducing-nima-neural-image-assessment/
    """
    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the Neural Image Assessment with the provided configuration.

        Args:
            config (ExtractorConfig): Configuration object for the image evaluator.
        """
        self._model = _ResNetModel.get_model(config)

    def evaluate_images(self, images: list[np.ndarray]) -> list[float]:
        """
        Evaluate a batch of images using the NIMA model, and return the results.

        Args:
            images (list[np.ndarray]): Batch of numpy array images to be evaluated.

        Returns:
            list[float]: List of scores corresponding to the input images.
        """
        logger.info("Evaluating images...")
        img_array = OpenCVImage.normalize_images(images)
        tensor = tf.convert_to_tensor(img_array)
        predictions = self._model.predict(tensor, batch_size=len(images), verbose=0)
        weights = _ResNetModel.prediction_weights
        scores = [self._calculate_weighted_mean(prediction, weights) for prediction in predictions]
        self._check_scores(images, scores)
        logger.info("Images batch evaluated.")
        return scores

    @staticmethod
    def _calculate_weighted_mean(prediction: np.array, weights: np.array = None) -> float:
        """
        Calculate the weighted mean of the prediction to get final image score.
        For example model InceptionResNetV2 returns 10 prediction scores for each image.
        We want to calculate weighted mean from that classification scores to calculate
        image final score. First classification score is less important and last is most.

        Args:
            prediction (np.array): Array of classification scores.

        Returns:
            float: Weighted mean of the prediction.
        """
        if weights is None:
            weights = np.ones_like(prediction)  # Default weights, equally distribute importance
        weighted_mean = np.sum(prediction * weights) / np.sum(weights)
        return weighted_mean


class _NIMAModel(ABC):
    """Abstract base class for the NIMA models. Uses a singleton pattern
    to manage a unique instance of the models.
    This is helper class for NeuralImageAssessment class.
    """
    class DownloadingModelWeightsError(Exception):
        """Error raised when there's an issue with downloading model weights."""
    _config = None
    _model = None

    @classmethod
    def get_model(cls, config: ExtractorConfig) -> Model:
        """
        Get the NIMA model instance, downloading the weights if necessary.

        Args:
            config (ExtractorConfig): Configuration object for the model.

        Returns:
            Model: NIMA model instance.
        """
        if cls._model is None:
            cls._config = config
            model_weights_path = cls._get_model_weights()
            cls._model = cls._create_model(model_weights_path)
        return cls._model

    @classmethod
    @abstractmethod
    def _create_model(cls, model_weights_path: Path) -> Model:
        """
        Create the NIMA model with the provided weights.

        Args:
            model_weights_path (Path): Path to the model weights.

        Returns:
            Model: NIMA model instance.
        """

    @classmethod
    def _get_model_weights(cls) -> Path:
        """
        Get the path to the model weights, downloading them if necessary.

        Returns:
            Path: Path to the model weights.
        """
        model_weights_directory = cls._config.weights_directory
        logger.info("Searching for model weights in weights directory: %s", model_weights_directory)
        model_weights_path = Path(model_weights_directory) / cls._config.weights_filename
        if not model_weights_path.is_file():
            logger.debug("Can't find model weights in weights directory: %s", model_weights_directory)
            cls._download_model_weights(model_weights_path)
        else:
            logger.debug(f"Model weights loaded from: {model_weights_path}")
        return model_weights_path

    @classmethod
    def _download_model_weights(cls, weights_path: Path) -> None:
        """
        Download the model weights from the specified URL.

        Args:
            weights_path (Path): Path to save the downloaded weights.

        Raises:
            cls.DownloadingModelWeightsError: If there's an issue downloading the weights.
        """
        url = f"{cls._config.weights_repo_url}{cls._config.weights_filename}"
        logger.debug("Downloading model weights from ulr: %s", url)
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            weights_path.parent.mkdir(parents=True, exist_ok=True)
            weights_path.write_bytes(response.content)
            logger.debug(f"Model weights downloaded and saved to %s", weights_path)
        else:
            message_error = f"Failed to download the weights: HTTP status code {response.status_code}"
            logger.error(message_error)
            raise cls.DownloadingModelWeightsError(message_error)


class _ResNetModel(_NIMAModel):
    """
    Implements the specific InceptionResNetV2-based NIMA model.
    This is helper class for NeuralImageAssessment class.
    """
    prediction_weights = np.arange(1, 11, 1)

    @classmethod
    def _create_model(cls, model_weights_path: Path) -> Model:
        """
        Create the InceptionResNetV2-based NIMA model with the provided weights.

        Args:
            model_weights_path (Path): Path to the model weights.

        Returns:
            Model: NIMA model instance.
        """
        base_model = InceptionResNetV2(
            input_shape=(224, 224, 3), include_top=False,
            pooling="avg", weights=None
        )
        processed_output = Dropout(0.75)(base_model.output)
        final_output = Dense(10, activation="softmax")(processed_output)
        model = Model(inputs=base_model.input, outputs=final_output)
        model.load_weights(model_weights_path)
        logger.debug("Model loaded successfully.")
        return model
