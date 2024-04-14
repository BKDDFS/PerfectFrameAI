import os

import shutil
import pytest

from app.top_frames_selector import TopFramesSelector

current_directory = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(current_directory, "test_files/best_frames")
OUTPUT_FOLDER = os.path.join(current_directory, "test_files/top_frames")


@pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_top_frames_selector():
    # restart environment after previous test
    assert os.path.isdir(INPUT_FOLDER)
    files = os.listdir(INPUT_FOLDER)
    found_top_frame_files = [file for file in files if file.startswith("best_frame_") and file.endswith(".jpg")]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in OUTPUT_FOLDER"
    if os.path.isdir(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    assert not os.path.isdir(OUTPUT_FOLDER), "OUTPUT_FOLDER was not removed"
    os.makedirs(OUTPUT_FOLDER)

    selector = TopFramesSelector(OUTPUT_FOLDER)
    selector.process(INPUT_FOLDER)

    files = os.listdir(OUTPUT_FOLDER)
    found_top_frame_files = [file for file in files if file.startswith("best_frame_") and file.endswith(".jpg")]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in OUTPUT_FOLDER"
