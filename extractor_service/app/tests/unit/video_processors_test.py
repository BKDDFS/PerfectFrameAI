import pytest

from app.video_processors import OpenCVVideo


@pytest.fixture
def opencv():
    opencv = OpenCVVideo()
    return opencv
