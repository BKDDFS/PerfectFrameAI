"""E2E test for top_images_extractor using testcontainers."""

import requests

from tests.e2e.conftest import cleanup_output_dir, wait_for_extraction_complete


def test_top_images_extractor(extractor_service):
    """Test top_images_extractor endpoint via docker-compose service."""
    base_url = extractor_service["base_url"]
    input_dir = extractor_service["input_dir"]
    output_dir = extractor_service["output_dir"]

    # Verify input image exists
    input_image = input_dir / "test_image.jpg"
    assert input_image.is_file(), "Test image not found in input directory"

    # Cleanup and verify empty
    cleanup_output_dir(output_dir)
    assert len(list(output_dir.glob("image_*.jpg"))) == 0, "Output dir not empty"

    # Call extractor API
    response = requests.post(
        f"{base_url}/v2/extractors/top_images_extractor",
        json={},
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
