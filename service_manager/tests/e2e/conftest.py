from pathlib import Path

import pytest

from ..common import (
    files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)  # import fixtures from common.py


@pytest.fixture(scope="module")
def start_script_path():
    base_path = Path(__file__).parent.parent.parent.parent
    start_script_path = base_path / "start.py"
    return start_script_path
