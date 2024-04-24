from pathlib import Path

import pytest
from fastapi import HTTPException, BackgroundTasks
from unittest.mock import patch, MagicMock
from extractor_service.app.extractor_manager import ExtractorManager
from extractor_service.app.schemas import ExtractorConfig

current_directory = Path.cwd()
CONFIG = ExtractorConfig(
    input_directory=current_directory,
    output_directory=current_directory,
)


@pytest.fixture
def manager():
    manager = ExtractorManager(CONFIG)
    return manager


def test_get_active_extractor(manager):
    assert manager.active_extractor is None


@patch("extractor_service.app.extractors.ExtractorFactory.get_extractor")
@patch("extractor_service.app.extractor_manager.ExtractorManager.check_is_already_extracting")
def test_start_extractor(mock_checking, mock_get_extractor, manager):
    extractor_name = "some_extractor"
    mock_extractor_class = MagicMock()
    mock_background_tasks = MagicMock(spec=BackgroundTasks)
    mock_get_extractor.return_value = mock_extractor_class

    message = manager.start_extractor(mock_background_tasks, extractor_name)

    mock_checking.assert_called_once()
    mock_get_extractor.assert_called_once_with(extractor_name)
    mock_background_tasks.add_task.assert_called_once_with(
        manager._ExtractorManager__run_extractor,
        mock_extractor_class
    )
    expected_message = f"'{extractor_name}' started."
    assert message == expected_message, "The return message does not match expected."


@patch("extractor_service.app.extractors.BestFramesExtractor")
def test_run_extractor(mock_extractor, manager):
    mock_extractor.return_value.process = MagicMock()
    mock_extractor.__name__ = MagicMock()

    manager._ExtractorManager__run_extractor(mock_extractor)

    mock_extractor.assert_called_once()


def test_check_is_already_evaluating_true(manager):
    manager._ExtractorManager__active_extractor = "active_evaluator"
    expected_error_massage = (
        f"Extractor '{manager.active_extractor}' is already running. "
        f"You can run only one extractor at the same time. "
        f"Wait until the evaluator is done before run next process."
    )

    with pytest.raises(HTTPException, match=expected_error_massage) as exc_info:
        manager.check_is_already_extracting()

    assert exc_info.value.status_code == 409
