import logging
from pathlib import Path

import pytest

from service_manager.service_initializer import ServiceInitializer


def test_directory_check_valid(tmp_path):
    assert ServiceInitializer._check_directory(str(tmp_path)) == tmp_path


def test_check_invalid_directory(caplog):
    invalid_directory = Path("/invalid/input")
    error_massage = f"Invalid directory path: {str(invalid_directory)}"

    with pytest.raises(NotADirectoryError), \
            caplog.at_level(logging.ERROR):
        ServiceInitializer._check_directory(str(invalid_directory))

    assert error_massage in caplog.text, "Invalid logging."
    