import pytest

from extractor_service.app.video_processors import OpenCVVideo


@pytest.fixture
def opencv():
    opencv = OpenCVVideo()