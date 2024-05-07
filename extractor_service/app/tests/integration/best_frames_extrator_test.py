from app.extractors import BestFramesExtractor
from app.schemas import ExtractorConfig


# @pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_best_frames_extractor(setup_best_frames_extractor_env):
    input_directory, output_directory, expected_video_path = setup_best_frames_extractor_env
    config = ExtractorConfig(input_directory=input_directory, output_directory=output_directory)

    extractor = BestFramesExtractor(config)
    extractor.process()

    found_best_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.name.endswith(".jpg")
    ]
    assert len(found_best_frame_files) > 0, "No files meeting the criteria were found in output_directory"
    assert expected_video_path.is_file(), "Video file name was not changed as expected"
