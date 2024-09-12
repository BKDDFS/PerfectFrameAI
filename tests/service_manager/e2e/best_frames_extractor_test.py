import os
import subprocess
import sys

import pytest


@pytest.mark.skipif("CI" in os.environ, reason="Test skipped in GitHub Actions.")
def test_best_frames_extractor(setup_best_frames_extractor_env, start_script_path):
    input_directory, output_directory, expected_video_path = setup_best_frames_extractor_env
    command = [
        sys.executable, str(start_script_path), "best_frames_extractor",
        "--input_dir", str(input_directory),
        "--output_dir", str(output_directory),
        "--build",
        "--cpu"
    ]

    subprocess.run(command)

    found_best_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.suffix == ".jpg"
    ]
    assert len(found_best_frame_files) > 0, "No files meeting the criteria were found in output_directory"
    assert expected_video_path.is_file(), "Video file name was not changed as expected"
