import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import cv2
import pytest

from extractor_service.app.video_processors import OpenCVVideo


@patch.object(cv2, "VideoCapture")
def test_get_video_capture_success(mock_cap):
    test_path = MagicMock(spec=Path)
    mock_video = MagicMock()
    mock_video.isOpened.return_value = True
    mock_cap.return_value = mock_video

    with OpenCVVideo._video_capture(test_path) as video:
        assert video.isOpened() is True

    mock_video.release.assert_called_once()


@patch.object(cv2, "VideoCapture")
def test_get_video_capture_failure(mock_cap):
    test_path = MagicMock(spec=Path)
    mock_video = MagicMock()
    mock_video.isOpened.return_value = False
    mock_cap.return_value = mock_video

    with pytest.raises(OpenCVVideo.CantOpenVideoCapture):
        with OpenCVVideo._video_capture(test_path):
            pass

    mock_video.release.assert_called_once()


@pytest.fixture
def mock_video():
    video = MagicMock()
    video.get.return_value = 30
    video.read.side_effect = [(True, "frame1"), (True, "frame2"), (True, "frame3"), (False, None)]
    return video


@pytest.mark.parametrize("batch_size, expected_num_batches", [
    (1, 3),
    (2, 2),
    (3, 1),
])
@patch.object(OpenCVVideo, '_video_capture')
@patch.object(OpenCVVideo, '_get_video_attribute')
@patch.object(OpenCVVideo, '_read_next_frame')
def test_get_next_video_frames(mock_read, mock_get_attribute, mock_video_cap,
                               batch_size, expected_num_batches, caplog):
    video_path = MagicMock()
    mock_video = MagicMock()
    frames_number = 3
    mock_get_attribute.side_effect = lambda video, attribute_id, value_name: \
        frames_number if "total frames" in value_name else 1
    mock_video_cap.return_value.__enter__.return_value = mock_video
    mock_read.side_effect = lambda video, idx: f"frame{idx // 30}"

    with caplog.at_level(logging.DEBUG):
        frames_generator = OpenCVVideo.get_next_frames(video_path, batch_size)
        batches = list(frames_generator)

    assert len(batches) == expected_num_batches, "Number of batches does not match expected"
    for batch in batches:
        assert len(batch) <= batch_size, "Batch size is larger than expected"
    assert mock_video_cap.called
    assert mock_get_attribute.call_count == 2
    mock_get_attribute.assert_any_call(mock_video, cv2.CAP_PROP_FPS, "frame rate")
    mock_get_attribute.assert_any_call(mock_video, cv2.CAP_PROP_FRAME_COUNT, "total frames")
    assert mock_read.call_count == 3

    assert "Frame appended to frames batch." in caplog.text
    assert "Got full frames batch." in caplog.text
    if batch_size % frames_number and frames_number > expected_num_batches * batch_size:
        assert "Returning last frames batch." in caplog.text


@pytest.mark.parametrize("read_return", ((True, "frame"), (False, None)))
@patch.object(OpenCVVideo, "_check_video_capture")
def test_read_next_frame(mock_check_cap, read_return, caplog):
    mock_cap = MagicMock(spec=cv2.VideoCapture)
    mock_cap.read = MagicMock(return_value=read_return)
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


@patch.object(OpenCVVideo, "_check_video_capture")
def test_get_video_attribute(mock_check_cap, caplog):
    mock_cap = MagicMock(spec=cv2.VideoCapture)
    attribute_id = cv2.CAP_PROP_FRAME_COUNT
    value_name = "total frames"
    total_frames = 24.6
    mock_cap.get.return_value = total_frames

    with caplog.at_level(logging.DEBUG):
        result = OpenCVVideo._get_video_attribute(mock_cap, attribute_id, value_name)

    mock_check_cap.assert_called_once_with(mock_cap)
    assert f"Got input video {value_name}: {total_frames}" in caplog.text
    assert result == 25


@patch.object(OpenCVVideo, "_check_video_capture")
def test_get_video_attribute_invalid(mock_check_cap, caplog):
    mock_cap = MagicMock(spec=cv2.VideoCapture)
    attribute_id = cv2.CAP_PROP_FRAME_COUNT
    value_name = "total frames"
    total_frames = -24.6
    mock_cap.get.return_value = total_frames
    expected_message = f"Invalid {value_name} retrieved: {total_frames}."

    with caplog.at_level(logging.ERROR), \
            pytest.raises(ValueError, match=expected_message):
        OpenCVVideo._get_video_attribute(mock_cap, attribute_id, value_name)

    mock_check_cap.assert_called_once_with(mock_cap)
    assert expected_message in caplog.text


def test_check_video_capture(caplog):
    mock_cap = MagicMock(spec=cv2.VideoCapture)
    mock_cap.isOpened.return_value = False
    error_message = ("Invalid video capture object or object not opened. "
                     "Probably video capture closed at some point.")

    with caplog.at_level(logging.ERROR), \
            pytest.raises(ValueError, match=error_message):
        OpenCVVideo._check_video_capture(mock_cap)

    assert error_message in caplog.text
