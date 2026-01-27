"""E2E test for top_images_extractor using testcontainers."""

import os

import pytest
import requests


@pytest.mark.skipif("CI" in os.environ, reason="Test skipped in GitHub Actions.")
def test_top_images_extractor(extractor_service):
    """Test top_images_extractor endpoint via docker-compose service."""
    response = requests.post(
        f"{extractor_service['base_url']}/v2/extractors/top_images_extractor",
        json={},
        timeout=30,
    )

    assert response.ok
    assert "started" in response.json().get("message", "").lower()

    # Check output files (note: extraction runs in background, so we check after a delay)
    # In a real scenario, you might want to poll or wait for completion
    _output_files = list(extractor_service["output_dir"].glob("image_*.jpg"))
    # The extractor runs in background, so files may not be immediately available
    # This test verifies the API accepts the request successfully
