"""
This module provides abstract class for creating image evaluators and image evaluators.
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
import requests
import tensorflow as tf
from tensorflow import convert_to_tensor
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense, Dropout

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
    def evaluate_images(self, images: np.ndarray) -> list[float]:
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
    """
    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the Neural Image Assessment with the provided configuration.

        Args:
            config (ExtractorConfig): Configuration object for the image evaluator.
        """
        self._model = _ResNetModel.get_model(config)

    def evaluate_images(self, images: np.ndarray) -> list[float]:
        """
        Evaluate a batch of images using the NIMA model, and return the results.

        Args:
            images (np.ndarray): Batch of numpy ndarray images to be evaluated.

        Returns:
            list[float]: List of scores corresponding to the input images.
        """
        logger.info("Evaluating images...")
        tensor = convert_to_tensor(images)
        batch_size = images.shape[0]
        predictions = self._model.predict(tensor, batch_size=batch_size, verbose=0)
        weights = _ResNetModel.get_prediction_weights()
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
    """
    Abstract base class for the NIMA models. Uses a singleton pattern
    to manage a unique instance of the models.
    This is helper class for NeuralImageAssessment class.
    """
    class DownloadingModelWeightsError(Exception):
        """Error raised when there's an issue with downloading model weights."""

    _config = None
    _model = None

    @classmethod
    def reset(cls) -> None:
        """Resets class for using new model and config."""
        cls._model = None
        cls._config = None

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
        logger.info("Searching for model weights in weights directory: %s",
                    model_weights_directory)
        model_weights_path = Path(model_weights_directory) / cls._config.weights_filename
        if not model_weights_path.is_file():
            logger.debug("Can't find model weights in weights directory: %s",
                         model_weights_directory)
            cls._download_model_weights(model_weights_path)
        else:
            logger.debug("Model weights loaded from: %s", model_weights_path)
        return model_weights_path

    @classmethod
    def _download_model_weights(cls, weights_path: Path, timeout: int = 10) -> None:
        """
        Download the model weights from the specified URL.

        Args:
            weights_path (Path): Path to save the downloaded weights.
            timeout (int): Timeout for the request in seconds.

        Raises:
            cls.DownloadingModelWeightsError: If there's an issue downloading the weights.
        """
        url = f"{cls._config.weights_repo_url}{cls._config.weights_filename}"
        logger.debug("Downloading model weights from ulr: %s", url)
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        if response.status_code == 200:
            weights_path.parent.mkdir(parents=True, exist_ok=True)
            weights_path.write_bytes(response.content)
            logger.debug("Model weights downloaded and saved to %s", weights_path)
        else:
            error_message = (f"Failed to download the weights: HTTP status code "
                             f"{response.status_code}")
            logger.error(error_message)
            raise cls.DownloadingModelWeightsError(error_message)


class _ResNetModel(_NIMAModel):
    """
    Implements the specific InceptionResNetV2-based NIMA model.
    This is helper class for NeuralImageAssessment class.
    """
    _prediction_weights = np.arange(1, 11)
    _input_shape = (224, 224, 3)
    _dropout_rate = 0.75
    _num_classes = 10

    @classmethod
    def get_prediction_weights(cls):
        """
        Getter for prediction weights.
        Weights are for calculating weighted mean from model predictions.
        """
        return cls._prediction_weights

    @classmethod
    def _create_model(cls, model_weights_path: Path) -> Model:
        """
        Create the InceptionResNetV2-based NIMA model with the provided weights.

        Args:
            model_weights_path (Path): Path to the model weights.

        Returns:
            Model: NIMA model instance.
        """
        base_model = tf.keras.applications.InceptionResNetV2(
            input_shape=cls._input_shape, include_top=False,
            pooling="avg", weights=None
        )
        processed_output = Dropout(cls._dropout_rate)(base_model.output)
        final_output = Dense(cls._num_classes, activation="softmax")(processed_output)
        model = Model(inputs=base_model.input, outputs=final_output)
        model.load_weights(model_weights_path)
        logger.debug("Model loaded successfully.")
        return model
