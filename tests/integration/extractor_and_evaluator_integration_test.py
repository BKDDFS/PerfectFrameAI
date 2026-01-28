import numpy as np
import onnxruntime as ort
import pytest

from perfectframe.image_evaluators import InceptionResNetNIMA
from perfectframe.schemas import ImageExtension


@pytest.mark.order(1)  # this test must be first because of hugging face limitations
def test_get_image_evaluator_download_weights_and_create_model(extractor, config):
    weights_path = config.weights_directory / config.weights_filename
    if weights_path.exists():
        weights_path.unlink()
    assert not weights_path.exists()

    evaluator = extractor._get_image_evaluator()

    assert isinstance(evaluator, InceptionResNetNIMA)
    assert isinstance(evaluator._session, ort.InferenceSession)
    assert weights_path.exists()


def test_evaluate_images(extractor, config):
    files = extractor._list_input_directory_files(ImageExtension)
    images = extractor._read_images(files)
    extractor._get_image_evaluator()
    normalized_images = extractor._normalize_images(images, config.input_size)
    result = extractor._evaluate_images(normalized_images)

    assert isinstance(result, np.ndarray)
