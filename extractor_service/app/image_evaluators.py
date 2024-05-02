"""
This module provides abstract class for creating image evaluators and image evaluators.
Image evaluators:
    - PyIQA: Removed in v2.0.
    - NIMA:
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2

from .image_processors import OpenCVImage
from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ImageEvaluator(ABC):
    """Abstraction class for creating image evaluators."""
    @abstractmethod
    def __init__(self, config: ExtractorConfig) -> None:
        """

        Args:
            config:
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


class NIMAModel:
    class DownloadingModelWeightsError(Exception):
        """"""
    _config = None
    _model = None

    @classmethod
    def get_model(cls, config: ExtractorConfig) -> Model:
        if cls._model is None:
            cls._config = config
            model_weights_path = cls._get_weights()
            cls._model = cls._create_model(model_weights_path)
        return cls._model

    @classmethod
    @abstractmethod
    def _create_model(cls, weights_path: Path) -> Model:
        """

        Args:
            weights_path:

        Returns:

        """

    @classmethod
    def _get_weights(cls) -> Path:
        weights_directory = cls._config.weights_directory
        logger.info("Searching for model weights in weights directory: %s", weights_directory)
        weights_path = Path(weights_directory) / cls._config.weights_filename
        if not weights_path.is_file():
            logger.debug("Can't find model weights in weights directory: %s", weights_directory)
            cls._download_weights(weights_path)
        else:
            logger.debug(f"Model weights loaded from: {weights_path}")
        return weights_path

    @classmethod
    def _download_weights(cls, weights_path: Path) -> None:
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


class InceptionResNetNIMA(NIMAModel):
    @classmethod
    def _create_model(cls, weights_path: Path) -> Model:
        base_model = InceptionResNetV2(
            input_shape=(224, 224, 3), include_top=False,
            pooling="avg", weights=None
        )
        processed_output = Dropout(0.75)(base_model.output)
        final_output = Dense(10, activation="softmax")(processed_output)
        model = Model(inputs=base_model.input, outputs=final_output)
        model.load_weights(weights_path)
        return model


class NeuralImageAssessment(ImageEvaluator):
    def __init__(self, config: ExtractorConfig) -> None:
        self._model = InceptionResNetNIMA.get_model(config)
        logger.debug("Model loaded successfully.")

    def evaluate_images(self, images: list[np.ndarray]) -> list[float]:
        """Evaluate a list of numpy array images using the model, and return the results."""
        scores = []
        for image in images:  # Register spilling where processing in batches. For loop +30% performance.
            image = OpenCVImage.normalize_image(image)
            prediction = self._model.predict(image, batch_size=1, verbose=0)[0]
            score = self._calculate_weighted_mean(prediction)
            scores.append(score)
        logger.info("Images batch evaluated.")
        self._check_scores(images, scores)
        return scores

    @staticmethod
    def _calculate_weighted_mean(scores: list[np.array]) -> float:
        weights = np.arange(1, 11, 1)
        weighted_mean = np.sum(scores * weights)
        return weighted_mean

    @staticmethod
    def _check_scores(images: list[np.ndarray], scores: list[float]) -> None:
        images_list_length = len(images)
        scores_list_length = len(scores)
        logger.debug("Scores: %s", scores)
        if images_list_length != scores_list_length:
            logger.warning("Scores and images lists lengths don't match!")
            logger.debug("Images list length: %s", images_list_length)
            logger.debug("Scores list length: %s", scores_list_length)
        else:
            logger.debug("Scores and images lists length: %s", images_list_length)
