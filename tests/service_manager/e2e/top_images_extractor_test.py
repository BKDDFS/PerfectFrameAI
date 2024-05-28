import subprocess
import sys


def test_top_images_extractor(setup_top_images_extractor_env, start_script_path):
    input_directory, output_directory = setup_top_images_extractor_env
    command = [
        sys.executable, str(start_script_path), "top_images_extractor",
        "--input_dir", input_directory,
        "--output_dir", output_directory,
        "--build",
        "--cpu"
    ]

    subprocess.run(command)

    found_top_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.name.endswith(".jpg")
    ]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in output_directory"
