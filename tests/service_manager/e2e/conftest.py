from pathlib import Path

import pytest

from tests.common import (best_frames_dir, files_dir,
                          setup_best_frames_extractor_env,
                          setup_top_images_extractor_env, top_images_dir)


@pytest.fixture(scope="module")
def start_script_path():
    base_path = Path(__file__).parent.parent.parent.parent
    print(base_path)
    start_script_path = base_path / "start.py"
    return start_script_path
