"""E2E test for best_frames_extractor using testcontainers."""

import requests

from tests.e2e.conftest import cleanup_output_dir, wait_for_extraction_complete


def test_best_frames_extractor(extractor_service):
    """Test best_frames_extractor endpoint via docker-compose service."""
    base_url = extractor_service["base_url"]
    input_dir = extractor_service["input_dir"]
    output_dir = extractor_service["output_dir"]

    # Cleanup and verify empty
    cleanup_output_dir(output_dir)
    assert len(list(output_dir.glob("image_*.jpg"))) == 0, "Output dir not empty"

    # Call extractor API
    response = requests.post(
        f"{base_url}/v2/extractors/best_frames_extractor",
        json={"all_frames": False},
        timeout=30,
    )

    assert response.ok
    assert "started" in response.json().get("message", "").lower()

    # Wait for extraction to complete
    extraction_completed = wait_for_extraction_complete(base_url, timeout=300)
    assert extraction_completed, "Extraction did not complete within timeout"

    # Verify output files were created
    output_files = list(output_dir.glob("image_*.jpg"))
    assert len(output_files) > 0, "No output files were created"

    # Verify video file was renamed (processed)
    expected_video_path = input_dir / "frames_extracted_test_video.mp4"
    assert expected_video_path.is_file(), "Video file was not renamed after processing"
