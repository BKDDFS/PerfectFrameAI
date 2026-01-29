from perfectframe.dependencies import Dependencies, get_dependencies
from perfectframe.image_evaluators import NIMAEvaluator
from perfectframe.image_processors import OpenCVImage
from perfectframe.schemas import ExtractorConfig
from perfectframe.video_processors import OpenCVVideo


def test_get_dependencies():
    dependencies = get_dependencies()

    assert isinstance(dependencies, Dependencies)
    assert dependencies.image_processor == OpenCVImage
    assert dependencies.video_processor == OpenCVVideo
    assert dependencies.evaluator == NIMAEvaluator
    assert isinstance(dependencies.config, ExtractorConfig)


def test_get_dependencies_with_custom_config():
    custom_config = ExtractorConfig(batch_size=100)

    dependencies = get_dependencies(custom_config)

    assert dependencies.config == custom_config
    assert dependencies.config.batch_size == custom_config.batch_size
