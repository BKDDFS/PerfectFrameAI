import os

import shutil
import pytest

from app.best_frames_extractor import BestFramesExtractor

current_directory = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(current_directory, "test_files")
OUTPUT_FOLDER = os.path.join(current_directory, "test_files/best_frames")


@pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_best_frames_extractor():
    expected_video_path = os.path.join(INPUT_FOLDER, "frames_extracted_test_video.mp4")
    video_path = os.path.join(INPUT_FOLDER, "test_video.mp4")

    # restart environment after previous test
    if os.path.isfile(expected_video_path):
        os.rename(expected_video_path, video_path)
    if os.path.isdir(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    assert not os.path.isdir(OUTPUT_FOLDER), "OUTPUT_FOLDER was not removed"
    os.makedirs(OUTPUT_FOLDER)

    extractor = BestFramesExtractor(OUTPUT_FOLDER)
    extractor.process(INPUT_FOLDER)

    files = os.listdir(OUTPUT_FOLDER)
    found_best_frame_files = [file for file in files if file.startswith("best_frame_") and file.endswith(".jpg")]
    assert len(found_best_frame_files) > 0, "No files meeting the criteria were found in OUTPUT_FOLDER"

    assert os.path.isfile(expected_video_path), "Video file name was not changed as expected"
