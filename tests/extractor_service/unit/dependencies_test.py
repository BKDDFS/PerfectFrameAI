from extractor_service.app.dependencies import (ExtractorDependencies,
                                                get_evaluator,
                                                get_extractor_dependencies,
                                                get_image_processor,
                                                get_video_processor)
from extractor_service.app.image_evaluators import InceptionResNetNIMA
from extractor_service.app.image_processors import OpenCVImage
from extractor_service.app.video_processors import OpenCVVideo


def test_get_image_processor():
    assert get_image_processor() == OpenCVImage


def test_get_video_processor():
    assert get_video_processor() == OpenCVVideo


def test_get_evaluator():
    assert get_evaluator() == InceptionResNetNIMA


def test_get_extractor_dependencies():
    dependencies = get_extractor_dependencies(
        image_processor=get_image_processor(),
        video_processor=get_video_processor(),
        evaluator=get_evaluator()
    )

    assert isinstance(dependencies, ExtractorDependencies)
    assert dependencies.image_processor == OpenCVImage
    assert dependencies.video_processor == OpenCVVideo
    assert dependencies.evaluator == InceptionResNetNIMA
