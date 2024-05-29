import pytest


# @pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_top_images_extractor_api(client, setup_top_images_extractor_env):
    input_directory, output_directory = setup_top_images_extractor_env
    extractor_name = "top_images_extractor"
    config = {
        "input_directory": str(input_directory),
        "output_directory": str(output_directory)
    }

    response = client.post(f"/v2/extractors/{extractor_name}", json=config)

    assert response.status_code == 200
    assert response.json()["message"] == f"'{extractor_name}' started."
    found_top_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.name.endswith(".jpg")
    ]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in output_directory"
