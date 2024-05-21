import pytest


# @pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_best_frames_extractor_api(client, setup_best_frames_extractor_env):
    input_directory, output_directory, expected_video_path = setup_best_frames_extractor_env
    extractor_name = "best_frames_extractor"
    config = {
        "input_directory": str(input_directory),
        "output_directory": str(output_directory)
    }

    response = client.post(f"/v2/extractors/{extractor_name}", json=config)

    assert response.status_code == 200
    assert response.json()["message"] == f"'{extractor_name}' started."
    found_best_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.suffix == ".jpg"
    ]
    assert len(found_best_frame_files) > 0, "No files meeting the criteria were found in output_directory"
    assert expected_video_path.is_file(), "Video file name was not changed as expected"
