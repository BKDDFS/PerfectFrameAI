import logging
from pathlib import Path

import cv2
import pytest

from perfectframe.video_processors import OpenCVVideo

TOTAL_FRAMES_ATTR = "total frames"


def test_get_video_capture_success(mocker):
    mock_cap = mocker.patch.object(cv2, "VideoCapture")
    test_path = mocker.MagicMock(spec=Path)
    mock_video = mocker.MagicMock()
    mock_video.isOpened.return_value = True
    mock_cap.return_value = mock_video

    with OpenCVVideo._video_capture(test_path) as video:
        assert video.isOpened() is True

    mock_video.release.assert_called_once()


def test_get_video_capture_failure(mocker):
    mock_cap = mocker.patch.object(cv2, "VideoCapture")
    test_path = mocker.MagicMock(spec=Path)
    mock_video = mocker.MagicMock()
    mock_video.isOpened.return_value = False
    mock_cap.return_value = mock_video

    with (
        pytest.raises(OpenCVVideo.CantOpenVideoCaptureError),
        OpenCVVideo._video_capture(test_path),
    ):
        # No additional operations are needed here, we are just testing the exception
        pass

    mock_video.release.assert_called_once()


@pytest.fixture
def mock_video(mocker):
    video = mocker.MagicMock()
    video.get.return_value = 30
    video.read.side_effect = [
        (True, "frame1"),
        (True, "frame2"),
        (True, "frame3"),
        (False, None),
    ]
    return video


@pytest.mark.parametrize(
    ("batch_size", "expected_num_batches"),
    [
        (1, 3),
        (2, 2),
        (3, 1),
    ],
)
def test_get_next_video_frames(
    mocker,
    batch_size,
    expected_num_batches,
    caplog,
):
    mock_read = mocker.patch.object(OpenCVVideo, "_read_next_frame")
    mock_get_attribute = mocker.patch.object(OpenCVVideo, "_get_video_attribute")
    mock_video_cap = mocker.patch.object(OpenCVVideo, "_video_capture")
    frame_rate_attr = "frame rate"
    video_path = mocker.MagicMock()
    mock_video = mocker.MagicMock()
    frames_number = 3

    def get_attribute_side_effect(_video, _attribute_id, value_name):
        return frames_number if TOTAL_FRAMES_ATTR in value_name else 1

    mock_get_attribute.side_effect = get_attribute_side_effect
    mock_video_cap.return_value.__enter__.return_value = mock_video

    def read_side_effect(_video, idx):
        return f"frame{idx // 30}"

    mock_read.side_effect = read_side_effect

    with caplog.at_level(logging.DEBUG):
        frames_generator = OpenCVVideo.get_next_frames(video_path, batch_size)
        batches = list(frames_generator)

    expected_attribute_calls = 2
    assert len(batches) == expected_num_batches, "Number of batches does not match expected"
    for batch in batches:
        assert len(batch) <= batch_size, "Batch size is larger than expected"
    assert mock_video_cap.called
    assert mock_get_attribute.call_count == expected_attribute_calls
    mock_get_attribute.assert_any_call(mock_video, cv2.CAP_PROP_FPS, frame_rate_attr)
    mock_get_attribute.assert_any_call(mock_video, cv2.CAP_PROP_FRAME_COUNT, TOTAL_FRAMES_ATTR)
    assert mock_read.call_count == frames_number

    assert "Frame appended to frames batch." in caplog.text
    assert "Got full frames batch." in caplog.text
    if batch_size % frames_number and frames_number > expected_num_batches * batch_size:
        assert "Returning last frames batch." in caplog.text


@pytest.mark.parametrize("read_return", [(True, "frame"), (False, None)])
def test_read_next_frame(mocker, read_return, caplog):
    mock_check_cap = mocker.patch.object(OpenCVVideo, "_check_video_capture")
    mock_cap = mocker.MagicMock(spec=cv2.VideoCapture)
    mock_cap.read = mocker.MagicMock(return_value=read_return)
    test_frame_index = 1
    with caplog.at_level(logging.WARNING):
        result = OpenCVVideo._read_next_frame(mock_cap, test_frame_index)

    mock_check_cap.assert_called_once_with(mock_cap)
    mock_cap.set.assert_called_once_with(cv2.CAP_PROP_POS_FRAMES, test_frame_index)
    mock_cap.read.assert_called_once()
    if read_return[0] is True:
        assert result == "frame"
    else:
        assert result is None
        assert f"Couldn't read frame with index: {test_frame_index}" in caplog.text


def test_get_video_attribute(mocker, caplog):
    mock_check_cap = mocker.patch.object(OpenCVVideo, "_check_video_capture")
    mock_cap = mocker.MagicMock(spec=cv2.VideoCapture)
    attribute_id = cv2.CAP_PROP_FRAME_COUNT
    value_name = TOTAL_FRAMES_ATTR
    total_frames = 24.6
    mock_cap.get.return_value = total_frames

    with caplog.at_level(logging.DEBUG):
        result = OpenCVVideo._get_video_attribute(mock_cap, attribute_id, value_name)

    expected_rounded = 25
    mock_check_cap.assert_called_once_with(mock_cap)
    assert f"Got input video {value_name}: {total_frames}" in caplog.text
    assert result == expected_rounded


def test_get_video_attribute_invalid(mocker, caplog):
    mock_check_cap = mocker.patch.object(OpenCVVideo, "_check_video_capture")
    mock_cap = mocker.MagicMock(spec=cv2.VideoCapture)
    attribute_id = cv2.CAP_PROP_FRAME_COUNT
    value_name = TOTAL_FRAMES_ATTR
    total_frames = -24.6
    mock_cap.get.return_value = total_frames
    expected_message = f"Invalid {value_name} retrieved: {total_frames}."

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match=expected_message),
    ):
        OpenCVVideo._get_video_attribute(mock_cap, attribute_id, value_name)

    mock_check_cap.assert_called_once_with(mock_cap)
    assert expected_message in caplog.text


def test_check_video_capture(mocker, caplog):
    mock_cap = mocker.MagicMock(spec=cv2.VideoCapture)
    mock_cap.isOpened.return_value = False
    error_message = (
        "Invalid video capture object or object not opened. "
        "Probably video capture closed at some point."
    )

    with caplog.at_level(logging.ERROR), pytest.raises(ValueError, match=error_message):
        OpenCVVideo._check_video_capture(mock_cap)

    assert error_message in caplog.text
