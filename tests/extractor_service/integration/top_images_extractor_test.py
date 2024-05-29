from extractor_service.app.extractors import TopImagesExtractor
from extractor_service.app.schemas import ExtractorConfig


# @pytest.mark.skip(reason="Test time-consuming and dependent on hardware performance")
def test_top_frames_extractor(setup_top_images_extractor_env, dependencies):
    input_directory, output_directory = setup_top_images_extractor_env
    config = ExtractorConfig(input_directory=input_directory, output_directory=output_directory)

    selector = TopImagesExtractor(config, dependencies.image_processor,
                                  dependencies.video_processor, dependencies.evaluator)
    selector.process()

    found_top_frame_files = [
        file for file in output_directory.iterdir()
        if file.name.startswith("image_") and file.name.endswith(".jpg")
    ]
    assert len(found_top_frame_files) > 0, "No files meeting the criteria were found in output_directory"
