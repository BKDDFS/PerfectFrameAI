import numpy as np
import pytest
from tensorflow.keras.models import Model

from app.image_evaluators import InceptionResNetNIMA


@pytest.mark.order(1)  # this test must be first because of hugging face limitations
def test_get_image_evaluator_download_weights_and_create_model(extractor, config):
    weights_path = config.weights_directory / config.weights_filename
    if weights_path.exists():
        weights_path.unlink()
    assert not weights_path.exists()

    evaluator = extractor._get_image_evaluator()

    isinstance(evaluator, InceptionResNetNIMA)
    isinstance(evaluator._model, Model)
    assert weights_path.exists()


def test_evaluate_images(extractor, config):
    files = extractor._list_input_directory_files(config.images_extensions)
    images = extractor._read_images(files)
    extractor._get_image_evaluator()
    result = extractor._evaluate_images(images)

    assert isinstance(result, np.ndarray)
